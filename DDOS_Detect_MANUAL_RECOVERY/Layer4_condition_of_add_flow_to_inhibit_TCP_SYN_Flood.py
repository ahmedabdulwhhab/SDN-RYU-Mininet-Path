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


###################


from ryu.lib.packet import in_proto
from ryu.lib.packet import ipv4
from ryu.lib.packet import icmp
from ryu.lib.packet import tcp
from ryu.lib.packet import udp
###############
from operator import attrgetter
from datetime import datetime
from ryu.app import simple_switch_13
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub
##################


from ryu.base.app_manager import RyuApp
from ryu.controller.ofp_event import EventOFPSwitchFeatures
from ryu.controller.handler import set_ev_cls
from ryu.controller.handler import CONFIG_DISPATCHER
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.ofproto.ofproto_v1_2 import OFPG_ANY
from ryu.ofproto.ofproto_v1_3 import OFP_VERSION
from ryu.lib.mac import haddr_to_bin
###################

class SimpleSwitch13(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch13, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.datapaths = {}
        self.monitor_thread = hub.spawn(self._monitor)
        self.fields = {'time':'','datapath':'','in-port':'','ipv4_src':'','ipv4_dst':'','out-port':'','total_packets':0,'total_bytes':0,'tp_src':0,'tp_dst':0}
        self.match_miss_flow_entry = ""
        self.actions_miss_flow_entry = ""


    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        match = parser.OFPMatch()
        self.match_miss_flow_entry = match
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.actions_miss_flow_entry = actions                                          
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions, buffer_id=None, idle=0, hard=0):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    idle_timeout=idle, hard_timeout=hard,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    idle_timeout=idle, hard_timeout=hard,
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
            return
        dst = eth.dst
        src = eth.src

        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})

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
                protocol = ip.proto
                
                
                                # match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP,
                                # ipv4_src=srcip,
                                # ipv4_dst=dstip,
                                # in_port =in_port
                                # )

                # if ICMP Protocol
                if protocol == in_proto.IPPROTO_ICMP:
                    t = pkt.get_protocol(icmp.icmp)
                    match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP,in_port=in_port,
                                            ipv4_src=srcip, ipv4_dst=dstip,
                                            ip_proto=protocol,icmpv4_code=t.code,
                                            icmpv4_type=t.type)

                #  if TCP Protocol
                elif protocol == in_proto.IPPROTO_TCP:
                    t = pkt.get_protocol(tcp.tcp)
                    match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP,in_port=in_port,
                                            ipv4_src=srcip, ipv4_dst=dstip,
                                            ip_proto=protocol,
                                            tcp_src=t.src_port, tcp_dst=t.dst_port,)

                #  If UDP Protocol
                elif protocol == in_proto.IPPROTO_UDP:
                    u = pkt.get_protocol(udp.udp)
                    match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP,in_port=in_port,
                                            ipv4_src=srcip, ipv4_dst=dstip,
                                            ip_proto=protocol,
                                            udp_src=u.src_port, udp_dst=u.dst_port,)

                # verify if we have a valid buffer_id, if yes avoid to send both
                # flow_mod & packet_out
                if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                    self.add_flow(datapath, 10, match, actions, msg.buffer_id, idle=20, hard=100)
                    return
                else:
                    self.add_flow(datapath, 10, match, actions, idle=20, hard=100)
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
        dp = self.datapaths[ev.msg.datapath.id]
        tp_src=0
        tp_dst=0
        ip_to_port={}
        boolean_match_ok=False




        #self.logger.info('body is ', body)
        # self.logger.info('time      datapath    dpid    '
                         # 'in-port  ipv4_src     ipv4_dst    '
                         # 'out-port total_packets  total_bytes      tcp_src      tcp_dst')


        # self.logger.info('---------------- '
                         # '-------- ----------------- '
                         # '-------- -------- --------')
        for stat in sorted([flow for flow in body if (flow.priority == 10) ], key=lambda flow:
            (flow.match['eth_type'],flow.match['ipv4_src'],flow.match['ipv4_dst'],flow.match['ip_proto'])):
        


        
            ip_src = stat.match['ipv4_src']
            ip_dst = stat.match['ipv4_dst']
            ip_proto = stat.match['ip_proto']
            
            ip_to_port.setdefault(ip_dst, {})            
            if stat.match['ip_proto'] == 1:
                icmp_code = stat.match['icmpv4_code']
                icmp_type = stat.match['icmpv4_type']

            elif stat.match['ip_proto'] == 6:
                tp_src = stat.match['tcp_src']
                tp_dst = stat.match['tcp_dst']

            elif stat.match['ip_proto'] == 17:
                tp_src = stat.match['udp_src']
                tp_dst = stat.match['udp_dst']
            #print details of flows
            self.fields['time'] = datetime.utcnow().strftime('%s')
            self.fields['datapath'] = ev.msg.datapath.id
            self.fields['in-port'] = stat.match['in_port']
            self.fields['ipv4_src'] = stat.match['ipv4_src']
            self.fields['ipv4_dst'] = stat.match['ipv4_dst']
            self.fields['out-port'] = stat.instructions[0].actions[0].port
            self.fields['total_packets'] = stat.packet_count
            self.fields['total_bytes'] = stat.byte_count
            self.fields['tcp_src'] = tp_src
            self.fields['tcp_dst'] = tp_dst


            # learn an ip address to avoid FLOOD next time.
            if stat.match['in_port'] in ip_to_port[ip_dst]:
                ip_to_port[ip_dst][stat.match['in_port']] = ip_to_port[ip_dst][stat.match['in_port']] + 1    #add 1
            else:
                ip_to_port[ip_dst][stat.match['in_port']] = 1
            
            # self.logger.info('data\t%s\t%x\t%x\t%s\t%s\t%x\t%d\t%d\t%d\t%d',self.fields['time'],self.fields['datapath'],self.fields['in-port'],
                                 # self.fields['ipv4_src'],self.fields['ipv4_dst'],self.fields['out-port'],self.fields['total_packets'],
                                 # self.fields['total_bytes'],self.fields['tcp_src'],self.fields['tcp_dst'])

            boolean_match_ok=True
        
      
        if(boolean_match_ok):
            #self.logger.info('ip_to_port ip_to_port[%s][%d]  is %d',ip_dst,self.fields['in-port'],ip_to_port[ip_dst][stat.match['in_port']])
            #self.logger.info('ip_to_port ip_to_port[%s][%d]  is %d',ip_dst,self.fields['in-port'],ip_to_port[ip_dst][stat.match['in_port']])
            self.logger.info('datapath %s' ,self.fields['datapath'])
            #print("ip_to_port ",ip_to_port)
            for key, values in ip_to_port.items():
                for i in values:
                    self.logger.info('ip_to_port [%s] : %d = %d',key, i,ip_to_port[key][i])  
                    if(ip_to_port[key][i] > 100):
                        #self.send_miss_flow_entry_again()
                        #datapath= self.fields['datapath']
                        print("datapath = ",ev.msg.datapath.id)
                        parser = dp.ofproto_parser
                        ofproto = dp.ofproto

                        match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP,in_port=stat.match['in_port'],
                                            ipv4_dst=self.fields['ipv4_dst'],
                                            
                                            )
                        self.add_flow(dp, 11, match, [], idle=20, hard=100)

        
        

##############new code
   



    #send miss flow entry again
    def send_miss_flow_entry_again(self): 
            for datapath in self.datapaths.values():
                #print("switches are ",datapath)
                #datapath = self.datapaths[dp]
                [self.remove_flows(datapath, n) for n in [0, 1]]    
            for datapath in self.datapaths.values():
                #print("switches are ",datapath)
                en_clear_flow_entry =  False
                self.add_flow(datapath, 0, self.match_miss_flow_entry, self.actions_miss_flow_entry) 

      
    
    def remove_flows(self, datapath, table_id):
        """Removing all flow entries."""
        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto
        empty_match = parser.OFPMatch()
        instructions = []
        flow_mod = self.remove_table_flows(datapath, table_id,
                                        empty_match, instructions)
        print ("deleting all flow entries in table ", table_id)
        datapath.send_msg(flow_mod)
    

    def remove_table_flows(self, datapath, table_id, match, instructions):
        """Create OFP flow mod message to remove flows from table."""
        ofproto = datapath.ofproto
        flow_mod = datapath.ofproto_parser.OFPFlowMod(datapath, 0, 0, table_id,
                                                      ofproto.OFPFC_DELETE, 0, 0,
                                                      1,
                                                      ofproto.OFPCML_NO_BUFFER,
                                                      ofproto.OFPP_ANY,
                                                      OFPG_ANY, 0,
                                                      match, instructions)
        return flow_mod

                
