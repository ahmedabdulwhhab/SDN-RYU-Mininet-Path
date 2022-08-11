# Copyright (C) 2011 Nippon Telegraph and Telephone Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.


#sudo ryu-manager  /home/ubuntu/sdn/projects/wifi/app1.py --observe-links --ofp-tcp-listen-port 6634



from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types

from ryu.lib.packet import ipv4

###############
from operator import attrgetter
from datetime import datetime
from ryu.app import simple_switch_13
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub
##################

class SimpleSwitch13(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch13, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.datapaths = {}
        self.monitor_thread = hub.spawn(self._monitor)
        self.fields = {'time':'','datapath':'','in-port':'','eth_src':'','eth_dst':'','out-port':'','total_packets':0,'total_bytes':0}


    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # install table-miss flow entry
        #
        # We specify NO BUFFER to max_len of the output action due to
        # OVS bug. At this moment, if we specify a lesser number, e.g.,
        # 128, OVS will send Packet-In with invalid buffer_id and
        # truncated packet data. In that case, we cannot output packets
        # correctly.  The bug has been fixed in OVS v2.1.0.
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        # If you hit this you might want to increase
        # the "miss_send_length" of your switch
        if ev.msg.msg_len < ev.msg.total_len:
            self.logger.debug("packet truncated: only %s of %s bytes",
                              ev.msg.msg_len, ev.msg.total_len)
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # ignore lldp packet
            return
        dst = eth.dst
        src = eth.src

        dpid = format(datapath.id, "d").zfill(16)
        self.mac_to_port.setdefault(dpid, {})

        self.logger.info("packet in %s %s %s %s", dpid, src, dst, in_port)

        # learn a mac address to avoid FLOOD next time.
        self.mac_to_port[dpid][src] = in_port

        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]

        # install a flow to avoid packet_in next time
        if out_port != ofproto.OFPP_FLOOD:
            # check IP Protocol and create a match for IP
            if eth.ethertype == ether_types.ETH_TYPE_IP:
                ip = pkt.get_protocol(ipv4.ipv4)
                srcip = ip.src
                dstip = ip.dst
                match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP,
                                ipv4_src=srcip,
                                ipv4_dst=dstip,
                                in_port =in_port
                                )
                # verify if we have a valid buffer_id, if yes avoid to send both
                # flow_mod & packet_out
                if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                    self.add_flow(datapath, 10, match, actions, msg.buffer_id)
                    return
                else:
                    self.add_flow(datapath, 10, match, actions)
        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)
##############new code
    @set_ev_cls(ofp_event.EventOFPStateChange,
                [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        datapath = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            if datapath.id not in self.datapaths:
                self.logger.debug('register datapath: %016x', datapath.id)
                self.datapaths[datapath.id] = datapath
        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.datapaths:
                self.logger.debug('unregister datapath: %016x', datapath.id)
                del self.datapaths[datapath.id]

    def _monitor(self):
        while True:
            for dp in self.datapaths.values():
                self._request_stats(dp)
            hub.sleep(1)

    def _request_stats(self, datapath):
        self.logger.debug('send stats request: %016x', datapath.id)
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        req = parser.OFPFlowStatsRequest(datapath)
        datapath.send_msg(req)

        #req = parser.OFPPortStatsRequest(datapath, 0, ofproto.OFPP_ANY)
        #datapath.send_msg(req)


    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def _flow_stats_reply_handler(self, ev):
        body = ev.msg.body
        
        #self.logger.info('body is ', body)
        #self.logger.info('time      datapath    dpid    '
        #                 'in-port  ipv4_src     ipv4_dst    '
        #                 'out-port total_packets  total_bytes')


        #self.logger.info('---------------- '
        #                 '-------- ----------------- '
        #                 '-------- -------- --------')
        for stat in sorted([flow for flow in body if flow.priority == 10],
                           key=lambda flow: (flow.match['in_port'],
                                             flow.match['ipv4_dst'])):
            #print details of flows
            self.fields['time'] = datetime.utcnow().strftime('%s')
            self.fields['datapath'] = ev.msg.datapath.id
            self.fields['in-port'] = stat.match['in_port']
            self.fields['eth_src'] = stat.match['ipv4_src']
            self.fields['eth_dst'] = stat.match['ipv4_dst']
            self.fields['out-port'] = stat.instructions[0].actions[0].port
            self.fields['total_packets'] = stat.packet_count
            self.fields['total_bytes'] = stat.byte_count
            self.logger.info('data\t%s\t%x\t%x\t%s\t%s\t%x\t%d\t%d',self.fields['time'],self.fields['datapath'],self.fields['in-port'],self.fields['eth_src'],self.fields['eth_dst'],self.fields['out-port'],self.fields['total_packets'],self.fields['total_bytes'])



"""
Arguments: ([OFPFlowStats(byte_count=240,cookie=0,duration_nsec=371000000,duration_sec=184,flags=0,hard_timeout=0,idle_timeout=0,instructions=[OFPInstructionActions(actions=[OFPActionOutput(len=16,max_len=65535,port=4294967293,type=0)],len=24,type=4)],length=96,match=OFPMatch(oxm_fields={'eth_dst': '01:80:c2:00:00:0e', 'eth_type': 35020}),packet_count=4,priority=65535,table_id=0), OFPFlowStats(byte_count=98,cookie=0,duration_nsec=207000000,duration_sec=16,flags=0,hard_timeout=0,idle_timeout=0,instructions=[OFPInstructionActions(actions=[OFPActionOutput(len=16,max_len=65509,port=4,type=0)],len=24,type=4)],length=112,match=OFPMatch(oxm_fields={'in_port': 2, 'eth_type': 2048, 'ipv4_src': '10.0.0.3', 'ipv4_dst': '10.0.0.5'}),packet_count=1,priority=10,table_id=0), OFPFlowStats(byte_count=98,cookie=0,duration_nsec=194000000,duration_sec=16,flags=0,hard_timeout=0,idle_timeout=0,instructions=[OFPInstructionActions(actions=[OFPActionOutput(len=16,max_len=65509,port=2,type=0)],len=24,type=4)],length=112,match=OFPMatch(oxm_fields={'in_port': 4, 'eth_type': 2048, 'ipv4_src': '10.0.0.5', 'ipv4_dst': '10.0.0.3'}),packet_count=1,priority=10,table_id=0), OFPFlowStats(byte_count=98,cookie=0,duration_nsec=169000000,duration_sec=16,flags=0,hard_timeout=0,idle_timeout=0,instructions=[OFPInstructionActions(actions=[OFPActionOutput(len=16,max_len=65509,port=4,type=0)],len=24,type=4)],length=112,match=OFPMatch(oxm_fields={'in_port': 2, 'eth_type': 2048, 'ipv4_src': '10.0.0.3', 'ipv4_dst': '10.0.0.4'}),packet_count=1,priority=10,table_id=0), OFPFlowStats(byte_count=98,cookie=0,duration_nsec=153000000,duration_sec=16,flags=0,hard_timeout=0,idle_timeout=0,instructions=[OFPInstructionActions(actions=[OFPActionOutput(len=16,max_len=65509,port=2,type=0)],len=24,type=4)],length=112,match=OFPMatch(oxm_fields={'in_port': 4, 'eth_type': 2048, 'ipv4_src': '10.0.0.4', 'ipv4_dst': '10.0.0.3'}),packet_count=1,priority=10,table_id=0), OFPFlowStats(byte_count=98,cookie=0,duration_nsec=126000000,duration_sec=16,flags=0,hard_timeout=0,idle_timeout=0,instructions=[OFPInstructionActions(actions=[OFPActionOutput(len=16,max_len=65509,port=3,type=0)],len=24,type=4)],length=112,match=OFPMatch(oxm_fields={'in_port': 2, 'eth_type': 2048, 'ipv4_src': '10.0.0.3', 'ipv4_dst': '10.0.0.1'}),packet_count=1,priority=10,table_id=0), OFPFlowStats(byte_count=98,cookie=0,duration_nsec=111000000,duration_sec=16,flags=0,hard_timeout=0,idle_timeout=0,instructions=[OFPInstructionActions(actions=[OFPActionOutput(len=16,max_len=65509,port=2,type=0)],len=24,type=4)],length=112,match=OFPMatch(oxm_fields={'in_port': 3, 'eth_type': 2048, 'ipv4_src': '10.0.0.1', 'ipv4_dst': '10.0.0.3'}),packet_count=1,priority=10,table_id=0), OFPFlowStats(byte_count=98,cookie=0,duration_nsec=87000000,duration_sec=16,flags=0,hard_timeout=0,idle_timeout=0,instructions=[OFPInstructionActions(actions=[OFPActionOutput(len=16,max_len=65509,port=1,type=0)],len=24,type=4)],length=112,match=OFPMatch(oxm_fields={'in_port': 2, 'eth_type': 2048, 'ipv4_src': '10.0.0.3', 'ipv4_dst': '10.0.0.2'}),packet_count=1,priority=10,table_id=0), OFPFlowStats(byte_count=98,cookie=0,duration_nsec=81000000,duration_sec=16,flags=0,hard_timeout=0,idle_timeout=0,instructions=[OFPInstructionActions(actions=[OFPActionOutput(len=16,max_len=65509,port=2,type=0)],len=24,type=4)],length=112,match=OFPMatch(oxm_fields={'in_port': 1, 'eth_type': 2048, 'ipv4_src': '10.0.0.2', 'ipv4_dst': '10.0.0.3'}),packet_count=1,priority=10,table_id=0), OFPFlowStats(byte_count=98,cookie=0,duration_nsec=44000000,duration_sec=16,flags=0,hard_timeout=0,idle_timeout=0,instructions=[OFPInstructionActions(actions=[OFPActionOutput(len=16,max_len=65509,port=3,type=0)],len=24,type=4)],length=112,match=OFPMatch(oxm_fields={'in_port': 2, 'eth_type': 2048, 'ipv4_src': '10.0.0.3', 'ipv4_dst': '10.0.0.101'}),packet_count=1,priority=10,table_id=0), OFPFlowStats(byte_count=98,cookie=0,duration_nsec=989000000,duration_sec=15,flags=0,hard_timeout=0,idle_timeout=0,instructions=[OFPInstructionActions(actions=[OFPActionOutput(len=16,max_len=65509,port=2,type=0)],len=24,type=4)],length=112,match=OFPMatch(oxm_fields={'in_port': 3, 'eth_type': 2048, 'ipv4_src': '10.0.0.101', 'ipv4_dst': '10.0.0.3'}),packet_count=1,priority=10,table_id=0), OFPFlowStats(byte_count=98,cookie=0,duration_nsec=955000000,duration_sec=15,flags=0,hard_timeout=0,idle_timeout=0,instructions=[OFPInstructionActions(actions=[OFPActionOutput(len=16,max_len=65509,port=3,type=0)],len=24,type=4)],length=112,match=OFPMatch(oxm_fields={'in_port': 2, 'eth_type': 2048, 'ipv4_src': '10.0.0.3', 'ipv4_dst': '10.0.0.102'}),packet_count=1,priority=10,table_id=0), OFPFlowStats(byte_count=98,cookie=0,duration_nsec=930000000,duration_sec=15,flags=0,hard_timeout=0,idle_timeout=0,instructions=[OFPInstructionActions(actions=[OFPActionOutput(len=16,max_len=65509,port=2,type=0)],len=24,type=4)],length=112,match=OFPMatch(oxm_fields={'in_port': 3, 'eth_type': 2048, 'ipv4_src': '10.0.0.102', 'ipv4_dst': '10.0.0.3'}),packet_count=1,priority=10,table_id=0), OFPFlowStats(byte_count=98,cookie=0,duration_nsec=856000000,duration_sec=15,flags=0,hard_timeout=0,idle_timeout=0,instructions=[OFPInstructionActions(actions=[OFPActionOutput(len=16,max_len=65509,port=3,type=0)],len=24,type=4)],length=112,match=OFPMatch(oxm_fields={'in_port': 4, 'eth_type': 2048, 'ipv4_src': '10.0.0.5', 'ipv4_dst': '10.0.0.1'}),packet_count=1,priority=10,table_id=0), OFPFlowStats(byte_count=98,cookie=0,duration_nsec=843000000,duration_sec=15,flags=0,hard_timeout=0,idle_timeout=0,instructions=[OFPInstructionActions(actions=[OFPActionOutput(len=16,max_len=65509,port=4,type=0)],len=24,type=4)],length=112,match=OFPMatch(oxm_fields={'in_port': 3, 'eth_type': 2048, 'ipv4_src': '10.0.0.1', 'ipv4_dst': '10.0.0.5'}),packet_count=1,priority=10,table_id=0), OFPFlowStats(byte_count=98,cookie=0,duration_nsec=808000000,duration_sec=15,flags=0,hard_timeout=0,idle_timeout=0,instructions=[OFPInstructionActions(actions=[OFPActionOutput(len=16,max_len=65509,port=1,type=0)],len=24,type=4)],length=112,match=OFPMatch(oxm_fields={'in_port': 4, 'eth_type': 2048, 'ipv4_src': '10.0.0.5', 'ipv4_dst': '10.0.0.2'}),packet_count=1,priority=10,table_id=0), OFPFlowStats(byte_count=98,cookie=0,duration_nsec=804000000,duration_sec=15,flags=0,hard_timeout=0,idle_timeout=0,instructions=[OFPInstructionActions(actions=[OFPActionOutput(len=16,max_len=65509,port=4,type=0)],len=24,type=4)],length=112,match=OFPMatch(oxm_fields={'in_port': 1, 'eth_type': 2048, 'ipv4_src': '10.0.0.2', 'ipv4_dst': '10.0.0.5'}),packet_count=1,priority=10,table_id=0), OFPFlowStats(byte_count=98,cookie=0,duration_nsec=757000000,duration_sec=15,flags=0,hard_timeout=0,idle_timeout=0,instructions=[OFPInstructionActions(actions=[OFPActionOutput(len=16,max_len=65509,port=3,type=0)],len=24,type=4)],length=112,match=OFPMatch(oxm_fields={'in_port': 4, 'eth_type': 2048, 'ipv4_src': '10.0.0.5', 'ipv4_dst': '10.0.0.101'}),packet_count=1,priority=10,table_id=0), OFPFlowStats(byte_count=98,cookie=0,duration_nsec=735000000,duration_sec=15,flags=0,hard_timeout=0,idle_timeout=0,instructions=[OFPInstructionActions(actions=[OFPActionOutput(len=16,max_len=65509,port=4,type=0)],len=24,type=4)],length=112,match=OFPMatch(oxm_fields={'in_port': 3, 'eth_type': 2048, 'ipv4_src': '10.0.0.101', 'ipv4_dst': '10.0.0.5'}),packet_count=1,priority=10,table_id=0), OFPFlowStats(byte_count=98,cookie=0,duration_nsec=687000000,duration_sec=15,flags=0,hard_timeout=0,idle_timeout=0,instructions=[OFPInstructionActions(actions=[OFPActionOutput(len=16,max_len=65509,port=3,type=0)],len=24,type=4)],length=112,match=OFPMatch(oxm_fields={'in_port': 4, 'eth_type': 2048, 'ipv4_src': '10.0.0.5', 'ipv4_dst': '10.0.0.102'}),packet_count=1,priority=10,table_id=0), OFPFlowStats(byte_count=98,cookie=0,duration_nsec=664000000,duration_sec=15,flags=0,hard_timeout=0,idle_timeout=0,instructions=[OFPInstructionActions(actions=[OFPActionOutput(len=16,max_len=65509,port=4,type=0)],len=24,type=4)],length=112,match=OFPMatch(oxm_fields={'in_port': 3, 'eth_type': 2048, 'ipv4_src': '10.0.0.102', 'ipv4_dst': '10.0.0.5'}),packet_count=1,priority=10,table_id=0), OFPFlowStats(byte_count=98,cookie=0,duration_nsec=610000000,duration_sec=15,flags=0,hard_timeout=0,idle_timeout=0,instructions=[OFPInstructionActions(actions=[OFPActionOutput(len=16,max_len=65509,port=3,type=0)],len=24,type=4)],length=112,match=OFPMatch(oxm_fields={'in_port': 4, 'eth_type': 2048, 'ipv4_src': '10.0.0.4', 'ipv4_dst': '10.0.0.1'}),packet_count=1,priority=10,table_id=0), OFPFlowStats(byte_count=98,cookie=0,duration_nsec=596000000,duration_sec=15,flags=0,hard_timeout=0,idle_timeout=0,instructions=[OFPInstructionActions(actions=[OFPActionOutput(len=16,max_len=65509,port=4,type=0)],len=24,type=4)],length=112,match=OFPMatch(oxm_fields={'in_port': 3, 'eth_type': 2048, 'ipv4_src': '10.0.0.1', 'ipv4_dst': '10.0.0.4'}),packet_count=1,priority=10,table_id=0), OFPFlowStats(byte_count=98,cookie=0,duration_nsec=562000000,duration_sec=15,flags=0,hard_timeout=0,idle_timeout=0,instructions=[OFPInstructionActions(actions=[OFPActionOutput(len=16,max_len=65509,port=1,type=0)],len=24,type=4)],length=112,match=OFPMatch(oxm_fields={'in_port': 4, 'eth_type': 2048, 'ipv4_src': '10.0.0.4', 'ipv4_dst': '10.0.0.2'}),packet_count=1,priority=10,table_id=0), OFPFlowStats(byte_count=98,cookie=0,duration_nsec=556000000,duration_sec=15,flags=0,hard_timeout=0,idle_timeout=0,instructions=[OFPInstructionActions(actions=[OFPActionOutput(len=16,max_len=65509,port=4,type=0)],len=24,type=4)],length=112,match=OFPMatch(oxm_fields={'in_port': 1, 'eth_type': 2048, 'ipv4_src': '10.0.0.2', 'ipv4_dst': '10.0.0.4'}),packet_count=1,priority=10,table_id=0), OFPFlowStats(byte_count=98,cookie=0,duration_nsec=509000000,duration_sec=15,flags=0,hard_timeout=0,idle_timeout=0,instructions=[OFPInstructionActions(actions=[OFPActionOutput(len=16,max_len=65509,port=3,type=0)],len=24,type=4)],length=112,match=OFPMatch(oxm_fields={'in_port': 4, 'eth_type': 2048, 'ipv4_src': '10.0.0.4', 'ipv4_dst': '10.0.0.101'}),packet_count=1,priority=10,table_id=0), OFPFlowStats(byte_count=98,cookie=0,duration_nsec=485000000,duration_sec=15,flags=0,hard_timeout=0,idle_timeout=0,instructions=[OFPInstructionActions(actions=[OFPActionOutput(len=16,max_len=65509,port=4,type=0)],len=24,type=4)],length=112,match=OFPMatch(oxm_fields={'in_port': 3, 'eth_type': 2048, 'ipv4_src': '10.0.0.101', 'ipv4_dst': '10.0.0.4'}),packet_count=1,priority=10,table_id=0), OFPFlowStats(byte_count=98,cookie=0,duration_nsec=434000000,duration_sec=15,flags=0,hard_timeout=0,idle_timeout=0,instructions=[OFPInstructionActions(actions=[OFPActionOutput(len=16,max_len=65509,port=3,type=0)],len=24,type=4)],length=112,match=OFPMatch(oxm_fields={'in_port': 4, 'eth_type': 2048, 'ipv4_src': '10.0.0.4', 'ipv4_dst': '10.0.0.102'}),packet_count=1,priority=10,table_id=0), OFPFlowStats(byte_count=98,cookie=0,duration_nsec=407000000,duration_sec=15,flags=0,hard_timeout=0,idle_timeout=0,instructions=[OFPInstructionActions(actions=[OFPActionOutput(len=16,max_len=65509,port=4,type=0)],len=24,type=4)],length=112,match=OFPMatch(oxm_fields={'in_port': 3, 'eth_type': 2048, 'ipv4_src': '10.0.0.102', 'ipv4_dst': '10.0.0.4'}),packet_count=1,priority=10,table_id=0), OFPFlowStats(byte_count=98,cookie=0,duration_nsec=343000000,duration_sec=15,flags=0,hard_timeout=0,idle_timeout=0,instructions=[OFPInstructionActions(actions=[OFPActionOutput(len=16,max_len=65509,port=1,type=0)],len=24,type=4)],length=112,match=OFPMatch(oxm_fields={'in_port': 3, 'eth_type': 2048, 'ipv4_src': '10.0.0.1', 'ipv4_dst': '10.0.0.2'}),packet_count=1,priority=10,table_id=0), OFPFlowStats(byte_count=98,cookie=0,duration_nsec=338000000,duration_sec=15,flags=0,hard_timeout=0,idle_timeout=0,instructions=[OFPInstructionActions(actions=[OFPActionOutput(len=16,max_len=65509,port=3,type=0)],len=24,type=4)],length=112,match=OFPMatch(oxm_fields={'in_port': 1, 'eth_type': 2048, 'ipv4_src': '10.0.0.2', 'ipv4_dst': '10.0.0.1'}),packet_count=1,priority=10,table_id=0), OFPFlowStats(byte_count=98,cookie=0,duration_nsec=170000000,duration_sec=15,flags=0,hard_timeout=0,idle_timeout=0,instructions=[OFPInstructionActions(actions=[OFPActionOutput(len=16,max_len=65509,port=3,type=0)],len=24,type=4)],length=112,match=OFPMatch(oxm_fields={'in_port': 1, 'eth_type': 2048, 'ipv4_src': '10.0.0.2', 'ipv4_dst': '10.0.0.101'}),packet_count=1,priority=10,table_id=0), OFPFlowStats(byte_count=98,cookie=0,duration_nsec=145000000,duration_sec=15,flags=0,hard_timeout=0,idle_timeout=0,instructions=[OFPInstructionActions(actions=[OFPActionOutput(len=16,max_len=65509,port=1,type=0)],len=24,type=4)],length=112,match=OFPMatch(oxm_fields={'in_port': 3, 'eth_type': 2048, 'ipv4_src': '10.0.0.101', 'ipv4_dst': '10.0.0.2'}),packet_count=1,priority=10,table_id=0), OFPFlowStats(byte_count=98,cookie=0,duration_nsec=108000000,duration_sec=15,flags=0,hard_timeout=0,idle_timeout=0,instructions=[OFPInstructionActions(actions=[OFPActionOutput(len=16,max_len=65509,port=3,type=0)],len=24,type=4)],length=112,match=OFPMatch(oxm_fields={'in_port': 1, 'eth_type': 2048, 'ipv4_src': '10.0.0.2', 'ipv4_dst': '10.0.0.102'}),packet_count=1,priority=10,table_id=0), OFPFlowStats(byte_count=98,cookie=0,duration_nsec=80000000,duration_sec=15,flags=0,hard_timeout=0,idle_timeout=0,instructions=[OFPInstructionActions(actions=[OFPActionOutput(len=16,max_len=65509,port=1,type=0)],len=24,type=4)],length=112,match=OFPMatch(oxm_fields={'in_port': 3, 'eth_type': 2048, 'ipv4_src': '10.0.0.102', 'ipv4_dst': '10.0.0.2'}),packet_count=1,priority=10,table_id=0), OFPFlowStats(byte_count=9059,cookie=0,duration_nsec=392000000,duration_sec=184,flags=0,hard_timeout=0,idle_timeout=0,instructions=[OFPInstructionActions(actions=[OFPActionOutput(len=16,max_len=65535,port=4294967293,type=0)],len=24,type=4)],length=80,match=OFPMatch(oxm_fields={}),packet_count=140,priority=0,table_id=0)],)
"""
