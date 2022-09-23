# https://github.com/al13mi/multipath-1/blob/master/ryu_multipath.py
# sudo rm ./sdn/ryu-controller/ah_learn_ryu_00/ryu_multipath.py && sudo vim  ./sdn/ryu-controller/ah_learn_ryu_00/ryu_multipath.py
# clear && ryu-manager ./sdn/ryu-controller/ah_learn_ryu_00/ryu_multipath.py --observe-links --ofp-tcp-listen-port 6633
# clear && sudo ryu-manager app2.py ../../sources/flowmanager/flowmanager.py  ryu.app.ofctl_rest --observe-links --ofp-tcp-listen-port 6633




#http://192.168.1.8:8080/home/topology.html
#sudo ovs-ofctl -O openflow13 dump-flows s1
#sudo ovs-ofctl -O openflow13 dump-groups s1

from ryu.base import app_manager
from ryu.controller import mac_to_port
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER,  DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.mac import haddr_to_bin
from ryu.lib.packet import packet
from ryu.lib.packet import arp
from ryu.lib.packet import ethernet
from ryu.lib.packet import ipv4
from ryu.lib.packet import ipv6
from ryu.lib.packet import ether_types
from ryu.ofproto import ether
from ryu.lib import mac, ip
from ryu.topology.api import get_switch, get_link
from ryu.app.wsgi import ControllerBase
from ryu.topology import event

from collections import defaultdict
from operator import itemgetter

import os
import random
import time




from ryu.base.app_manager import RyuApp
from ryu.controller.ofp_event import EventOFPSwitchFeatures
from ryu.controller.handler import set_ev_cls
from ryu.controller.handler import CONFIG_DISPATCHER
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.ofproto.ofproto_v1_2 import OFPG_ANY
from ryu.ofproto.ofproto_v1_3 import OFP_VERSION
from ryu.lib.mac import haddr_to_bin



# Cisco Reference bandwidth = 1 Gbps
REFERENCE_BW = 10000000

DEFAULT_BW = 10000000

MAX_PATHS = float('Inf')

idle_time=3000


# Ipv4 operation codes
IPV4_REQUEST = 1
IPV4_REPLY = 2
IPV4_REV_REQUEST = 3
IPV4_REV_REPLY = 4

class ProjectController(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(ProjectController, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.topology_api_app = self
        self.datapath_list = {}
        self.datapaths = {}
        self.arp_table = {}
        self.switches = []
        self.hosts = {}
        self.multipath_group_ids = {}
        self.group_ids = []
        self.adjacency = defaultdict(dict)
        self.bandwidths = defaultdict(lambda: defaultdict(lambda: DEFAULT_BW))
        self.en_clear_flow_entry = False
        self.disable_packet_in = False
        self.input_port=0
        self.actions_miss_flow_entry=""
        self.backup_path=""
        self.avoid_arp_function = False
        #Proxy arp table
        # arp table: for searching
        self.arp_table={}
        self.arp_table["10.0.0.1"] = "00:00:00:00:00:01"
        self.arp_table["10.0.0.2"] = "00:00:00:00:00:02"
        self.arp_table["10.0.0.3"] = "00:00:00:00:00:03"
        self.arp_table["10.0.0.4"] = "00:00:00:00:00:04"
        self.ipv4_opcode=0
        
        
    def get_paths(self, src, dst):
        '''
        Get all paths from src to dst using DFS algorithm    
        '''
        if src == dst:
            # host target is on the same switch
            return [[src]]
        paths = []
        stack = [(src, [src])]
        #print("self.adjacency ", self.adjacency)
        
        while stack:
            #print("get_pahs; stack = ",stack)
            (node, path) = stack.pop()
            #print( "(node, path), node = ",node, " path = ",path)
            
            for next in set(self.adjacency[node].keys()) - set(path):
                if next is dst:
                    paths.append(path + [next])
                else:
                    stack.append((next, path + [next]))
        #print("stack after while is ", stack)
        #print ("Available paths from src_switch", src, " to dst_switch", dst, " : ", paths)
        return paths

    def get_link_cost(self, s1, s2):
        '''
        Get the link cost between two switches 
        '''
        e1 = self.adjacency[s1][s2]
        e2 = self.adjacency[s2][s1]
        bl = min(self.bandwidths[s1][e1], self.bandwidths[s2][e2])
        ew = REFERENCE_BW/bl
        return ew

    def get_path_cost(self, path):
        '''
        Get the path cost
        '''
        cost = 0
        for i in range(len(path) - 1):
            cost += self.get_link_cost(path[i], path[i+1])
        return cost
       #get_optimal_paths(src_switch, dst_switch)
    def get_optimal_paths(self, src, dst): #src is switch, dst is switch
        '''
        Get the n-most optimal paths according to MAX_PATHS
        '''
        paths = self.get_paths(src, dst)
        paths_count = len(paths) if len(
            paths) < MAX_PATHS else MAX_PATHS
        return sorted(paths, key=lambda x: self.get_path_cost(x))[0:(paths_count)]

    def add_ports_to_paths(self, paths, first_port, last_port):
        '''
        Add the ports that connects the switches for all paths
        '''
        paths_p = []
        for path in paths:
            p = {}
            in_port = first_port
            for s1, s2 in zip(path[:-1], path[1:]):
                out_port = self.adjacency[s1][s2]
                p[s1] = (in_port, out_port)
                in_port = self.adjacency[s2][s1]
            p[path[-1]] = (in_port, last_port)
            paths_p.append(p)
        return paths_p

    def generate_openflow_gid(self):
        '''
        Returns a random OpenFlow group id
        '''
        n = random.randint(0, 2**32)
        while n in self.group_ids:
            n = random.randint(0, 2**32)
        return n

  #self.install_paths(      h1[0],       h1[1],      h2[0],       h2[1],   src_ip, dst_ip)
    def install_paths(self, src_switch, first_port, dst_switch, last_port, ip_src, ip_dst):
        computation_start = time.time()
        paths = self.get_optimal_paths(src_switch, dst_switch)
        #print("paths from src_switch  ",src_switch, " to dst_switch  ",dst_switch, " are ",paths)
        minimum_cost=0xffff
        pw = []
        for path in paths:
            pw.append(self.get_path_cost(path))
            #print (path, "cost = ", pw[len(pw) - 1])
            if(pw[len(pw) - 1] <minimum_cost):      minimum_cost = pw[len(pw) - 1]
        sum_of_pw = sum(pw)
        paths_with_ports = self.add_ports_to_paths(paths, first_port, last_port)
        switches_in_paths = set().union(*paths)
        #print("switches_in_paths is ", switches_in_paths)
        #print("Example for paths_with_ports [{1: (1, 2), 2: (1, 3)}, {1: (1, 3), 4: (1, 3), 3: (1, 3), 2: (2, 3)}] \n" ,"host path is from s1 port 1 to port 2 then you are now at s2 use port 1 to port 3 to connect to dest host")
        #print(" paths_with_ports is ", paths_with_ports)
        #for i in len(paths_with_ports):
        #    print("paths_with_ports[i]= ", paths_with_ports[i])
        single_path=paths_with_ports[0]
        print(" Single path from src switch to dst switch is ", single_path)
        key_val= [key_val for key_val in single_path.keys()]
        #print("****************************key_val of single path is ",key_val)
        
        #for j in range(len(key_val) ):
            #print("at j = " ,j ," key_val = ",key_val[j])
            #print("single_path   ", single_path[key_val[j]][0])
            
        
        #print("ip_src  = ",ip_src, " ip_dst = ",ip_dst)
        for j in range(len(key_val) ):
            #print("src_sw_dp = ",key_val[j])
            if(j== len(key_val)-1):
                #last switch in path
                #print("self.adjacency = ",self.adjacency)
                src_sw_dp = self.datapath_list[key_val[j]]
                mac= self.arp_table[ip_src]

                #print("src host is connected to port ", self.hosts[mac][key_val[len(key_val)-1]], " src_sw_dp = ",key_val[j])
                final_out = single_path[key_val[len(key_val)-1]][1]  #self.hosts[mac][key_val[len(key_val)-1]]
                #print("Last switch in the loop port number is ",final_out)
                src_sw_dp = self.datapath_list[key_val[j]]
                #print("Packet is recevied from port  ",self.input_port)
                ofp = src_sw_dp.ofproto
                ofp_parser = src_sw_dp.ofproto_parser
                match_ip = ofp_parser.OFPMatch(
                        eth_type=0x0800, 
                        ipv4_src=ip_src, 
                        ipv4_dst=ip_dst
                    )
                match_arp = ofp_parser.OFPMatch(
                        eth_type=0x0806, 
                        arp_spa=ip_src, 
                        arp_tpa=ip_dst
                    )
                    
                    
                #src switch flow entry
                actions = [ofp_parser.OFPActionOutput(final_out)]
                        
                self.en_clear_flow_entry=True
                #src switch flow entry
                self.add_flow(src_sw_dp, 32768, match_ip, actions)
                #self.add_flow(src_sw_dp, 1, match_arp, actions)
                ##############################################################
                #First switch in path
                dst_sw_dp = self.datapath_list[key_val[0]]
                final_out = single_path[key_val[0]][0]
                #print("first switch in the loop port number is ",final_out)
                 
                #print("initial ip is ",self.hosts)
                #print("Packet is recevied from port  ",self.input_port)
                ofp = src_sw_dp.ofproto
                ofp_parser = dst_sw_dp.ofproto_parser
                match_ip = ofp_parser.OFPMatch(
                        eth_type=0x0800, 
                        ipv4_src=ip_dst, 
                        ipv4_dst=ip_src
                    )
                match_arp = ofp_parser.OFPMatch(
                        eth_type=0x0806, 
                        arp_spa=ip_dst, 
                        arp_tpa=ip_src
                    )
                    
                    
                #src switch flow entry
                actions = [ofp_parser.OFPActionOutput(final_out)]
                        
                self.en_clear_flow_entry=True
                #src switch flow entry
                self.add_flow(dst_sw_dp, 32768, match_ip, actions)
                #self.add_flow(dst_sw_dp, 1, match_arp, actions)
                #j =j+5
                
                
            else:
                src_sw_dp = self.datapath_list[key_val[j]]
                #dst_sw_dp = self.datapath_list[key_val[j+1]] 
                #print("dst_sw_dp = ",dst_sw_dp)
                #print("out port from src switch is ",self.adjacency[key_val[j]][key_val[j+1]])
                #print("in port of dst  switch is ",self.adjacency[key_val[j+1]][key_val[j]])
                final_out= self.adjacency[key_val[j]][key_val[j+1]]
                ofp = src_sw_dp.ofproto
                ofp_parser = src_sw_dp.ofproto_parser
                match_ip = ofp_parser.OFPMatch(
                        eth_type=0x0800, 
                        ipv4_src=ip_src, 
                        ipv4_dst=ip_dst
                    )
                match_arp = ofp_parser.OFPMatch(
                        eth_type=0x0806, 
                        arp_spa=ip_src, 
                        arp_tpa=ip_dst
                    )
                    
                    
                #src switch flow entry
                actions = [ofp_parser.OFPActionOutput(final_out)]
                        
                self.en_clear_flow_entry=True
                #src switch flow entry
                self.add_flow(src_sw_dp, 32768, match_ip, actions)
                #self.add_flow(src_sw_dp, 1, match_arp, actions)
                
                #actions = [ofp_parser.OFPActionOutput(self.adjacency[key_val[j+1]][key_val[j]])]
                        
                #dst switch flow entry
                #self.add_flow(dst_sw_dp, 32768, match_ip, actions)
                #self.add_flow(dst_sw_dp, 1, match_arp, actions)            
                #self.add_flow(dp, 1, match_arp, actions)            
            
            
           
        
        """
        for node in switches_in_paths:
            print("inside for node in switches_in_paths, node = ", node)

            dp = self.datapath_list[node]
            ofp = dp.ofproto
            ofp_parser = dp.ofproto_parser

            ports = defaultdict(list)
            actions = []
            i = 0

            for path in paths_with_ports:
                print("inside path in paths_with_ports: path = ",path)
                if node in path:
                    in_port = path[node][0]
                    out_port = path[node][1]
                    if (out_port, pw[i]) not in ports[in_port]:
                        ports[in_port].append((out_port, pw[i]))
                i += 1
            print("ports is ",ports," \n sum_of_pw = ",sum_of_pw) 
            self.en_clear_flow_entry = True
            

            for in_port in ports:

                match_ip = ofp_parser.OFPMatch(
                    eth_type=0x0800, 
                    ipv4_src=ip_src, 
                    ipv4_dst=ip_dst
                )
                match_arp = ofp_parser.OFPMatch(
                    eth_type=0x0806, 
                    arp_spa=ip_src, 
                    arp_tpa=ip_dst
                )

                print ("Line 202 in_port = ",in_port)
                out_ports = ports[in_port]
                print ("out_ports = ",out_ports)

                if len(out_ports) > 1:
                    group_id = None
                    group_new = False

                    if (node, src_switch, dst_switch) not in self.multipath_group_ids:
                        group_new = True
                        self.multipath_group_ids[
                            node, src_switch, dst_switch] = self.generate_openflow_gid()
                    group_id = self.multipath_group_ids[node, src_switch, dst_switch]

                    buckets = []
                    print ("node at ",node," out ports : ",out_ports)
                    print("group_id = ",group_id)
                    for port, weight in out_ports:
                        bucket_weight =  int(round((1 - weight/sum_of_pw) * 100))
                        bucket_action = [ofp_parser.OFPActionOutput(port)]
                        buckets.append(
                            ofp_parser.OFPBucket(
                                weight=bucket_weight,
                                watch_port=ofp.OFPG_ANY, #port,
                                watch_group=ofp.OFPG_ANY,
                                actions=bucket_action
                            )
                        )

                    if group_new:
                        req = ofp_parser.OFPGroupMod(
                            dp, ofp.OFPGC_ADD, ofp.OFPGT_SELECT, group_id,
                            buckets
                        )
                        dp.send_msg(req)
                    else:
                        req = ofp_parser.OFPGroupMod(
                            dp, ofp.OFPGC_MODIFY, ofp.OFPGT_SELECT,
                            group_id, buckets)
                        dp.send_msg(req)

                    actions = [ofp_parser.OFPActionGroup(group_id)]
                    
                    self.en_clear_flow_entry=True
                    self.add_flow(dp, 32768, match_ip, actions)
                    self.add_flow(dp, 1, match_arp, actions)

                elif len(out_ports) == 1:
                    actions = [ofp_parser.OFPActionOutput(out_ports[0][0])]
                    self.en_clear_flow_entry=True
                    self.add_flow(dp, 32768, match_ip, actions)
                    self.add_flow(dp, 1, match_arp, actions)
        print ("Path installation finished in ", time.time() - computation_start )
        """
        return paths_with_ports[0][src_switch][1]

    def add_flow(self, datapath, priority, match, actions, buffer_id=None): #modify flow entry
        # print ("Adding flow ", match, actions)
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        #print("en_clear_flow_entry = ",self.en_clear_flow_entry)
        if buffer_id:
            if(self.en_clear_flow_entry):
                mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,idle_timeout=idle_time,#*datapath.id,
                                    instructions=inst)
            else:
                mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            if(self.en_clear_flow_entry):
                mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, idle_timeout=idle_time,#*datapath.id
                                    instructions=inst)
            else:
                mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match,instructions=inst)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER) #create miss flow entry then send it
    def _switch_features_handler(self, ev):
        #print ("switch_features_handler is called")
        datapath = ev.msg.datapath
        print ("switch_features_handler is called for ",datapath.id)
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        #print("actions for called switch miss flow entry is ",actions)                                  
        self.actions_miss_flow_entry = actions
        self.match_miss_flow_entry = match
        
        self.add_flow(datapath, 0, match, actions)

    @set_ev_cls(ofp_event.EventOFPPortDescStatsReply, MAIN_DISPATCHER)
    def port_desc_stats_reply_handler(self, ev):
        switch = ev.msg.datapath
        for p in ev.msg.body:
            self.bandwidths[switch.id][p.port_no] = p.curr_speed


    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        #print("msg is ", msg)
        in_port = msg.match['in_port']
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)
        #print("eth is ", eth)
        ethertype = eth.ethertype

        # process ARP 
        if ethertype == ether.ETH_TYPE_ARP:
            self.handle_arp(datapath, in_port, pkt)
            return


            
        if pkt.get_protocol(ipv6.ipv6):  # Drop the IPV6 Packets.
            match = parser.OFPMatch(eth_type=eth.ethertype)
            actions = []
            self.en_clear_flow_entry=False
            self.add_flow(datapath, 1, match, actions)
            return 

        # avoid broadcast from LLDP
        if eth.ethertype == 35020:
            return

        # process IP
        if ethertype == ether.ETH_TYPE_IP:          
            dst = eth.dst       #mac address of destination
            src = eth.src       #mac address of source
            dpid = datapath.id
            
    
            if src not in self.hosts:
                self.hosts[src] = (dpid, in_port)
                self.input_port = in_port
                print("Firest request comming form src ", src)
                #self.ipv4_opcode=IPV4_REQUEST
                self.store_current_src_mac=src
                #print("inside packetin, sel.hosts 'mac': (sw, port) is ",self.hosts)
                #print("inside packetin,  src not in self.hosts , dst is ",dst)
                #after first h2 ping -c1 h1
                #inside packetin, sel.hosts is  {'00:00:02:00:00:00': (3, 5)}
                #inside packetin,  src not in self.hosts  ff:ff:ff:ff:ff:ff
                #above mac is called key
                #value switch id 3;     host is located at port 5
            if dst not in self.hosts:
                self.ipv4_opcode=IPV4_REQUEST
                self.store_current_src_mac=src
            else:
                if(self.store_current_src_mac!=src):        #duplicate msg from flooding
                    self.ipv4_opcode=IPV4_REPLY
                    self.store_current_src_mac = dst
            out_port = ofproto.OFPP_FLOOD
            
            if pkt.get_protocol(ipv4.ipv4):  ##################### inhibit duplicate
                match = parser.OFPMatch(eth_type=eth.ethertype)  
                print(" eth.dst = ", eth.dst, " eth.src = ", eth.src)
                src_ip = pkt.get_protocol(ipv4.ipv4).src
                dst_ip = pkt.get_protocol(ipv4.ipv4).dst
                dst = eth.dst       #mac address of destination
                src = eth.src       #mac address of source
                dpid = datapath.id
                #self.arp_table[src_ip] = src
                print("ipv4 packet ", pkt.get_protocol(ipv4.ipv4))
                if (self.ipv4_opcode==IPV4_REPLY): #pkt.get_protocol(ipv4.ipv4).opcode == ipv4.ipv4_REPLY: # IF REPLY IS RECEIVED.
                    h1 = self.hosts[src]        #(dpid, in_port)
                    h2 = self.hosts[dst]        #(dpid, in_port)
                    out_port = self.install_paths(h1[0], h1[1], h2[0], h2[1], src_ip, dst_ip)
                    self.install_paths(h2[0], h2[1], h1[0], h1[1], dst_ip, src_ip)    
                    self.store_current_src_mac = "00"                    
                    print("ip_v4 Received ")    
                    #self.avoid_arp_function = True
                    #return
    
    
            #if(self.avoid_arp_function == True): return
            
            
    
    
    
    
    
            # if arp_pkt:
                # # print (dpid, pkt)
                # src_ip = arp_pkt.src_ip
                # dst_ip = arp_pkt.dst_ip
                # if arp_pkt.opcode == arp.ARP_REPLY: # IF REPLY IS RECEIVED.
                    # self.arp_table[src_ip] = src
                    # #print("arp_pkt.opcode == arp.ARP_REPLY , self.arp_table is ",self.arp_table)
                    # #key of arp_table is ip, value is src_mac
                    # h1 = self.hosts[src]        #(dpid, in_port)
                    # h2 = self.hosts[dst]        #(dpid, in_port)
                    # out_port = self.install_paths(h1[0], h1[1], h2[0], h2[1], src_ip, dst_ip)
                    # #self.disable_packet_in = True
                    # self.install_paths(h2[0], h2[1], h1[0], h1[1], dst_ip, src_ip) # reverse
                    # #self.disable_packet_in = False
                # elif arp_pkt.opcode == arp.ARP_REQUEST: #IF REQUEST IS GOING TO INITIATED.
                    # #لم يتم تجهيزه بعد
                    # #print(" #لم يتم تجهيزه بعد ")
                    # if dst_ip in self.arp_table:
                        # self.arp_table[src_ip] = src
                        # dst_mac = self.arp_table[dst_ip]
                        # h1 = self.hosts[src]
                        # h2 = self.hosts[dst_mac]
                        # #print("inside ARP_REQUEST h1= ", h1 ," h2= ",h2, " src_ip = ",src_ip, " dst_ip = ",dst_ip)
                        # out_port = self.install_paths(h1[0], h1[1], h2[0], h2[1], src_ip, dst_ip)
                        # #self.disable_packet_in = False
                        # self.install_paths(h2[0], h2[1], h1[0], h1[1], dst_ip, src_ip) # reverse
                        # #self.disable_packet_in = False
    
            # #print (pkt)
    
            actions = [parser.OFPActionOutput(out_port)]
    
            data = None
            if msg.buffer_id == ofproto.OFP_NO_BUFFER:
                data = msg.data
    
            out = parser.OFPPacketOut(
                datapath=datapath, buffer_id=msg.buffer_id, in_port=in_port,
                actions=actions, data=data)
            datapath.send_msg(out)



    # @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    # def _packet_in_handler(self, ev):
        # msg = ev.msg
        # datapath = msg.datapath
        # ofproto = datapath.ofproto
        # parser = datapath.ofproto_parser
        # in_port = msg.match['in_port']

        # pkt = packet.Packet(msg.data)
        # eth = pkt.get_protocol(ethernet.ethernet)
        # arp_pkt = pkt.get_protocol(arp.arp)

        # # avoid broadcast from LLDP
        # if eth.ethertype == 35020:
            # return
        # if self.disable_packet_in :
            # return

        # if pkt.get_protocol(ipv4.ipv4):  ##################### inhibit duplicate
            # match = parser.OFPMatch(eth_type=eth.ethertype)  
            # print(" eth.dst = ", eth.dst, " eth.src = ", eth.src)
            # src_ip = pkt.get_protocol(ipv4.ipv4).src
            # dst_ip = pkt.get_protocol(ipv4.ipv4).dst
            # dst = eth.dst       #mac address of destination
            # src = eth.src       #mac address of source
            # dpid = datapath.id
            # self.arp_table[src_ip] = src
            # h1 = self.hosts[src]        #(dpid, in_port)
            # h2 = self.hosts[dst]        #(dpid, in_port)
            # out_port = self.install_paths(h1[0], h1[1], h2[0], h2[1], src_ip, dst_ip)
            # out_port = self.install_paths(h2[0], h2[1], h1[0], h1[1], dst_ip, src_ip)            
            # print("ip_v4 Received ")    
            # #self.avoid_arp_function = True
            # return


        # #if(self.avoid_arp_function == True): return
        
        
        # if pkt.get_protocol(ipv6.ipv6):  # Drop the IPV6 Packets.
            # match = parser.OFPMatch(eth_type=eth.ethertype)
            # actions = []
            # self.en_clear_flow_entry=False
            # self.add_flow(datapath, 1, match, actions)
            # return None


        # dst = eth.dst       #mac address of destination
        # src = eth.src       #mac address of source
        # dpid = datapath.id
        

        # if src not in self.hosts:
            # self.hosts[src] = (dpid, in_port)
            # self.input_port = in_port
            # #print("inside packetin, sel.hosts 'mac': (sw, port) is ",self.hosts)
            # #print("inside packetin,  src not in self.hosts , dst is ",dst)
            # #after first h2 ping -c1 h1
            # #inside packetin, sel.hosts is  {'00:00:02:00:00:00': (3, 5)}
            # #inside packetin,  src not in self.hosts  ff:ff:ff:ff:ff:ff
            # #above mac is called key
            # #value switch id 3;     host is located at port 5

        # out_port = ofproto.OFPP_FLOOD

        # if arp_pkt:
            # # print (dpid, pkt)
            # src_ip = arp_pkt.src_ip
            # dst_ip = arp_pkt.dst_ip
            # if arp_pkt.opcode == arp.ARP_REPLY: # IF REPLY IS RECEIVED.
                # self.arp_table[src_ip] = src
                # #print("arp_pkt.opcode == arp.ARP_REPLY , self.arp_table is ",self.arp_table)
                # #key of arp_table is ip, value is src_mac
                # h1 = self.hosts[src]        #(dpid, in_port)
                # h2 = self.hosts[dst]        #(dpid, in_port)
                # out_port = self.install_paths(h1[0], h1[1], h2[0], h2[1], src_ip, dst_ip)
                # #self.disable_packet_in = True
                # self.install_paths(h2[0], h2[1], h1[0], h1[1], dst_ip, src_ip) # reverse
                # #self.disable_packet_in = False
            # elif arp_pkt.opcode == arp.ARP_REQUEST: #IF REQUEST IS GOING TO INITIATED.
                # #لم يتم تجهيزه بعد
                # #print(" #لم يتم تجهيزه بعد ")
                # if dst_ip in self.arp_table:
                    # self.arp_table[src_ip] = src
                    # dst_mac = self.arp_table[dst_ip]
                    # h1 = self.hosts[src]
                    # h2 = self.hosts[dst_mac]
                    # #print("inside ARP_REQUEST h1= ", h1 ," h2= ",h2, " src_ip = ",src_ip, " dst_ip = ",dst_ip)
                    # out_port = self.install_paths(h1[0], h1[1], h2[0], h2[1], src_ip, dst_ip)
                    # #self.disable_packet_in = False
                    # self.install_paths(h2[0], h2[1], h1[0], h1[1], dst_ip, src_ip) # reverse
                    # #self.disable_packet_in = False

        # #print (pkt)

        # actions = [parser.OFPActionOutput(out_port)]

        # data = None
        # if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            # data = msg.data

        # out = parser.OFPPacketOut(
            # datapath=datapath, buffer_id=msg.buffer_id, in_port=in_port,
            # actions=actions, data=data)
        # datapath.send_msg(out)

    """
        Methods to handle ARP. In this implementation the controller
        generates the ARP reply msg back to the host who initiate it.
        So the controller should parse out the ARP request;
        Search the ARP table for correponding dst MAC;
        Generate ARP reply;
        And finally use PacketOut Message to send back the ARP reply
    """
    def handle_arp(self, datapath, in_port, pkt):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # parse out the ethernet and arp packet
        eth_pkt = pkt.get_protocol(ethernet.ethernet)
        arp_pkt = pkt.get_protocol(arp.arp)
        # obtain the MAC of dst IP  
        arp_resolv_mac = self.arp_table[arp_pkt.dst_ip]

        ### generate the ARP reply msg, please refer RYU documentation
        ### the packet library section
	# ARP Reply Msg
        ether_hd = ethernet.ethernet(dst = eth_pkt.src, 
                                src = arp_resolv_mac, 
                                ethertype = ether.ETH_TYPE_ARP);
        arp_hd = arp.arp(hwtype=1, proto = 2048, hlen = 6, plen = 4,
                         opcode = 2, src_mac = arp_resolv_mac, 
                         src_ip = arp_pkt.dst_ip, dst_mac = eth_pkt.src,
                         dst_ip = arp_pkt.src_ip);
        arp_reply = packet.Packet()
        arp_reply.add_protocol(ether_hd)
        arp_reply.add_protocol(arp_hd)
        #print("arp_reply ", arp_reply)
        arp_reply.serialize()
        print("Executing ARP Reply IP ", arp_pkt.src_ip, " located at datapath.id ", datapath.id, " at port ", in_port)
        
        # send the Packet Out mst to back to the host who is initilaizing the ARP
        actions = [parser.OFPActionOutput(in_port)];
        out = parser.OFPPacketOut(datapath, ofproto.OFP_NO_BUFFER, 
                                  ofproto.OFPP_CONTROLLER, actions,
                                  arp_reply.data)
        datapath.send_msg(out)







    @set_ev_cls(event.EventSwitchEnter) #update datapath_list[dpid], o/p is self.datapath_list[switch.id]
    def switch_enter_handler(self, event):  
        switch = event.switch.dp
        ofp_parser = switch.ofproto_parser

        if switch.id not in self.switches:
            self.switches.append(switch.id)
            self.datapath_list[switch.id] = switch

            # Request port/link descriptions, useful for obtaining bandwidth
            req = ofp_parser.OFPPortDescStatsRequest(switch)
            switch.send_msg(req)

    @set_ev_cls(event.EventSwitchLeave, MAIN_DISPATCHER) #del datapath_list[dpid], del adjacency
    def switch_leave_handler(self, event):
        #print( event)
        switch = event.switch.dp.id
        if switch in self.switches:
            del self.switches[switch]
            del self.datapath_list[switch]
            del self.adjacency[switch]

    @set_ev_cls(event.EventLinkAdd, MAIN_DISPATCHER) #create self.adjacency
    def link_add_handler(self, event):
        s1 = event.link.src
        #print("EventLinkAdd ; event.link.src = ",s1)
        s2 = event.link.dst
        #print("EventLinkAdd ; event.link.dst = ",s2)
        self.adjacency[s1.dpid][s2.dpid] = s1.port_no
        self.adjacency[s2.dpid][s1.dpid] = s2.port_no
        #print("1: {4: 3, 2: 2} means details of switch s1 is connected to s4 via s1-eth3; and is connected to s2 via s1-eth2")
        #print("EventLinkAdd ; adjacency is ",self.adjacency)
        self.send_miss_flow_entry_again()        

    @set_ev_cls(event.EventLinkDelete, MAIN_DISPATCHER)
    def link_delete_handler(self, event):
        #print("EventLinkdelete ; event.link.src = ",event.link.src)
        #print("EventLinkdelete ; event.link.dst = ",event.link.dst)
        #print("val of  self.adjacency[event.link.src.dpid][event.link.dst.dpid] is ",self.adjacency[event.link.src.dpid][event.link.dst.dpid])
        del self.adjacency[event.link.src.dpid][event.link.dst.dpid]
        new_dic=self.adjacency
        key_val= [key_val for key_val in new_dic.keys()]
        #print("key_val = ",key_val)
        #del new_dic[event.link.src.dpid]
        #k = event.link.src.dpid
        #for key_val in new_dic.keys():
        #print( "new_dic = ",new_dic)
        self.send_miss_flow_entry_again()
        return
        
        
    #store all datapaths
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

                