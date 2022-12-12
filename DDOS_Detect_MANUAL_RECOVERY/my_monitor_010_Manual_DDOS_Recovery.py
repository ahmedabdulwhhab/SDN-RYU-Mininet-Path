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

# sudo mn -c ; sudo mn --controller=remote,ip=192.168.1.7:6633 --mac -i 10.0.0.0/24 --switch=ovsk,protocols=OpenFlow13 --topo=linear,4,5
# sudo mn -c ; sudo mn --controller=remote,ip=192.168.1.7:6633 --mac -i 10.0.0.0/24 --switch=ovsk,protocols=OpenFlow13 --topo=linear,5,6
# sudo mn -c ; sudo mn --controller=remote,ip=192.168.1.7:6633 --mac  -i 10.0.0.0/24 --switch=ovsk,protocols=OpenFlow13 --topo=single,16
# sudo mn -c; sudo mn --controller=remote,ip=192.168.1.7:6633 --mac -i 10.0.0.0/24 --switch=ovsk,protocols=OpenFlow13  --topo=tree,depth=2,fanout=3
# clear && sudo ryu-manager my_monitor_010_Manual_DDOS_Recovery.py   /home/ubuntu/sdn/sources/flowmanager/flowmanager.py  --observe-links --ofp-tcp-listen-port 6633
#sudo ovs-ofctl -O openflow13 dump-flows s1
#


from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types

from ryu.lib.packet import in_proto
from ryu.lib.packet import ipv4
from ryu.lib.packet import icmp
from ryu.lib.packet import tcp
from ryu.lib.packet import udp
from ryu.lib import hub
import sys


class SimpleSwitch13(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch13, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.datapaths = {}
        ###############################
        self.mac_ip_to_dp = {}            #dict
        self.ddos_oocurs=False
        self.src_of_DDOS =0     #src mac
        self.wait_time_after_DDOS = 0
        self.monitor_thread = hub.spawn(self._monitor)
        ###############################

    def _monitor(self):
        while True:
            if(self.ddos_oocurs ):
                self.wait_time_after_DDOS = self.wait_time_after_DDOS + 1
            else:
                self.wait_time_after_DDOS  = 0 
            if(self.wait_time_after_DDOS > 20):
                self.mac_ip_to_dp = {}            #dict
                self.ddos_oocurs=False
            hub.sleep(1)

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

        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})
		####################################
        self.mac_ip_to_dp.setdefault(src, {})           #src as key        
        if(self.src_of_DDOS == src) and self.ddos_oocurs:
            return          #during DDOS        
		####################################

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
            #########################################################
            if(len(self.mac_ip_to_dp[src]) > 5):
                    self.ddos_oocurs=True
                    print("DDos occur from src ", src)
                    match1 = parser.OFPMatch( eth_dst=dst, eth_src=src)
                    match2 = parser.OFPMatch( eth_src=src)     #block src only with low priority
                    self.add_flow(datapath, 114, match1, [],idle=30, hard=100*3)  					
                    for dp in self.datapaths.values():
                        if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                            self.add_flow(dp, 110, match1, [],msg.buffer_id, idle=30, hard=100*2)
                            self.add_flow(dp, 108, match2, [],msg.buffer_id, idle=30, hard=100*2)
							
                        else:
                            self.add_flow(dp, 110, match1, [],idle=30, hard=100*2)
                            self.add_flow(dp, 108, match2, [], idle=30, hard=100*2)
					
                    #import time
                    #time.sleep(20)
                    #print("sleep duration is finished")
                    return -2                                        
                                        #############################
            add_rule_to_switch =0
            # check IP Protocol and create a match for IP
            if eth.ethertype == ether_types.ETH_TYPE_IP:
                ip = pkt.get_protocol(ipv4.ipv4)
                srcip = ip.src
                dstip = ip.dst
                protocol = ip.proto
                self.mac_ip_to_dp[src][srcip]=0
                # if ICMP Protocol
                if protocol == in_proto.IPPROTO_ICMP:
                    match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP, ipv4_src=srcip, ipv4_dst=dstip, ip_proto=protocol)
                    add_rule_to_switch =1


            
                #  if TCP Protocol
                elif protocol == in_proto.IPPROTO_TCP:
                    t = pkt.get_protocol(tcp.tcp)
                    print("pkt_tcp.bits", t.bits)
                    if(t.bits >2):
                        match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP, ipv4_src=srcip, ipv4_dst=dstip, ip_proto=protocol, tcp_src=t.src_port, tcp_dst=t.dst_port,)                    
                        add_rule_to_switch =1
            
                #  If UDP Protocol 
                elif protocol == in_proto.IPPROTO_UDP:
                    u = pkt.get_protocol(udp.udp)
                    match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP, ipv4_src=srcip, ipv4_dst=dstip, ip_proto=protocol, udp_src=u.src_port, udp_dst=u.dst_port,)            
                    add_rule_to_switch =1
                # verify if we have a valid buffer_id, if yes avoid to send both
                # flow_mod & packet_out
                if  msg.buffer_id != ofproto.OFP_NO_BUFFER:
                    if(add_rule_to_switch):
                        self.add_flow(datapath, 1, match, actions, msg.buffer_id,idle =30, hard =60)
                    return
                else:
                    if(add_rule_to_switch):
                        self.add_flow(datapath, 1, match, actions,idle=30,hard =60)
        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)
