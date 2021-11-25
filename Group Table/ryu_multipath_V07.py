# https://github.com/al13mi/multipath-1/blob/master/ryu_multipath.py
# sudo rm ./sdn/ryu-controller/ah_learn_ryu_00/ryu_multipath.py && sudo vim  ./sdn/ryu-controller/ah_learn_ryu_00/ryu_multipath.py
# clear && ryu-manager ./sdn/ryu-controller/ah_learn_ryu_00/ryu_multipath.py --observe-links --ofp-tcp-listen-port 6633
#clear && sudo ryu-manager ./sdn/ryu-controller/ah_learn_ryu_00/ryu_multipath.py ./sdn/ryu-controller/flowmanager/flowmanager.py  --observe-links --ofp-tcp-listen-port 6633
#clear && sudo ryu-manager multi_path_controller.py ../../flowmanager/flowmanager.py  ryu.app.ofctl_rest --observe-links --ofp-tcp-listen-port 6633

#http://192.168.1.8:8080/home/topology.html
#sudo ovs-ofctl -O openflow13 dump-flows s1
#sudo ovs-ofctl -O openflow13 dump-groups s1

from ryu.base import app_manager
from ryu.controller import mac_to_port
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.mac import haddr_to_bin
from ryu.lib.packet import packet
from ryu.lib.packet import arp
from ryu.lib.packet import ethernet
from ryu.lib.packet import ipv4
from ryu.lib.packet import ipv6
from ryu.lib.packet import ether_types
from ryu.lib import mac, ip
from ryu.topology.api import get_switch, get_link
from ryu.app.wsgi import ControllerBase
from ryu.topology import event

from collections import defaultdict
from operator import itemgetter

import os
import random
import time

# Cisco Reference bandwidth = 1 Gbps
REFERENCE_BW = 10000000

DEFAULT_BW = 10000000

MAX_PATHS = float('Inf')

idle_time=10

class ProjectController(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(ProjectController, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.topology_api_app = self
        self.datapath_list = {}
        self.arp_table = {}
        self.switches = []
        self.hosts = {}
        self.multipath_group_ids = {}
        self.group_ids = []
        self.adjacency = defaultdict(dict)
        self.bandwidths = defaultdict(lambda: defaultdict(lambda: DEFAULT_BW))
        self.en_clear_flow_entry = False

    def get_paths(self, src, dst):
        '''
        Get all paths from src to dst using DFS algorithm    
        '''
        if src == dst:
            # host target is on the same switch
            return [[src]]
        paths = []
        stack = [(src, [src])]
        print("self.adjacency ", self.adjacency)
        
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
        print ("Available paths from src_switch", src, " to dst_switch", dst, " : ", paths)
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
        print("paths from src_switch  ",src_switch, " to dst_switch  ",dst_switch, " are ",paths)
        pw = []
        for path in paths:
            pw.append(self.get_path_cost(path))
            print (path, "cost = ", pw[len(pw) - 1])
        sum_of_pw = sum(pw)
        paths_with_ports = self.add_ports_to_paths(paths, first_port, last_port)
        switches_in_paths = set().union(*paths)
        print("switches_in_paths is ", switches_in_paths)
        print("Example for paths_with_ports [{1: (1, 2), 2: (1, 3)}, {1: (1, 3), 4: (1, 3), 3: (1, 3), 2: (2, 3)}] \n" ,
        "host path is from s1 port 1 to port 2 then you are now at s2 use port 1 to port 3 to connect to dest host")
        print(" paths_with_ports is ", paths_with_ports)

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
        return paths_with_ports[0][src_switch][1]

    def add_flow(self, datapath, priority, match, actions, buffer_id=None): #modify flow entry
        # print ("Adding flow ", match, actions)
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        print("en_clear_flow_entry = ",self.en_clear_flow_entry)
        if buffer_id:
            if(self.en_clear_flow_entry):
                mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,idle_timeout=idle_time*datapath.id,
                                    instructions=inst)
            else:
                mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            if(self.en_clear_flow_entry):
                mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, idle_timeout=idle_time*datapath.id,instructions=inst)
            else:
                mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match,instructions=inst)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER) #create miss flow entry then send it
    def _switch_features_handler(self, ev):
        print ("switch_features_handler is called")
        datapath = ev.msg.datapath
        print ("switch_features_handler is called for ",datapath.id)
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        print("actions for called switch miss flow entry is ",actions)                                  
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
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)
        arp_pkt = pkt.get_protocol(arp.arp)

        # avoid broadcast from LLDP
        if eth.ethertype == 35020:
            return

        if pkt.get_protocol(ipv6.ipv6):  # Drop the IPV6 Packets.
            match = parser.OFPMatch(eth_type=eth.ethertype)
            actions = []
            self.en_clear_flow_entry=False
            self.add_flow(datapath, 1, match, actions)
            return None

        dst = eth.dst       #mac address of destination
        src = eth.src       #mac address of source
        dpid = datapath.id

        if src not in self.hosts:
            self.hosts[src] = (dpid, in_port)
            print("inside packetin, sel.hosts 'mac': (sw, port) is ",self.hosts)
            print("inside packetin,  src not in self.hosts , dst is ",dst)
            #after first h2 ping -c1 h1
            #inside packetin, sel.hosts is  {'00:00:02:00:00:00': (3, 5)}
            #inside packetin,  src not in self.hosts  ff:ff:ff:ff:ff:ff
            #above mac is called key
            #value switch id 3;     host is located at port 5

        out_port = ofproto.OFPP_FLOOD

        if arp_pkt:
            # print (dpid, pkt)
            src_ip = arp_pkt.src_ip
            dst_ip = arp_pkt.dst_ip
            if arp_pkt.opcode == arp.ARP_REPLY: # IF REPLY IS RECEIVED.
                self.arp_table[src_ip] = src
                print("arp_pkt.opcode == arp.ARP_REPLY , self.arp_table is ",self.arp_table)
                #key of arp_table is ip, value is src_mac
                h1 = self.hosts[src]        #(dpid, in_port)
                h2 = self.hosts[dst]        #(dpid, in_port)
                out_port = self.install_paths(h1[0], h1[1], h2[0], h2[1], src_ip, dst_ip)
                self.install_paths(h2[0], h2[1], h1[0], h1[1], dst_ip, src_ip) # reverse
            elif arp_pkt.opcode == arp.ARP_REQUEST: #IF REQUEST IS GOING TO INITIATED.
                #لم يتم تجهيزه بعد
                if dst_ip in self.arp_table:
                    self.arp_table[src_ip] = src
                    dst_mac = self.arp_table[dst_ip]
                    h1 = self.hosts[src]
                    h2 = self.hosts[dst_mac]
                    out_port = self.install_paths(h1[0], h1[1], h2[0], h2[1], src_ip, dst_ip)
                    self.install_paths(h2[0], h2[1], h1[0], h1[1], dst_ip, src_ip) # reverse

        print (pkt)

        actions = [parser.OFPActionOutput(out_port)]

        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(
            datapath=datapath, buffer_id=msg.buffer_id, in_port=in_port,
            actions=actions, data=data)
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
        print( event)
        switch = event.switch.dp.id
        if switch in self.switches:
            del self.switches[switch]
            del self.datapath_list[switch]
            del self.adjacency[switch]

    @set_ev_cls(event.EventLinkAdd, MAIN_DISPATCHER) #create self.adjacency
    def link_add_handler(self, event):
        s1 = event.link.src
        print("EventLinkAdd ; event.link.src = ",s1)
        s2 = event.link.dst
        print("EventLinkAdd ; event.link.dst = ",s2)
        self.adjacency[s1.dpid][s2.dpid] = s1.port_no
        self.adjacency[s2.dpid][s1.dpid] = s2.port_no
        print("1: {4: 3, 2: 2} means details of switch s1 is connected to s4 via s1-eth3; and is connected to s2 via s1-eth2")
        print("EventLinkAdd ; adjacency is ",self.adjacency)

    @set_ev_cls(event.EventLinkDelete, MAIN_DISPATCHER)
    def link_delete_handler(self, event):
        print("EventLinkdelete ; event.link.src = ",event.link.src)
        print("EventLinkdelete ; event.link.dst = ",event.link.dst)
        #print("val of  self.adjacency[event.link.src.dpid][event.link.dst.dpid] is ",self.adjacency[event.link.src.dpid][event.link.dst.dpid])
        del self.adjacency[event.link.src.dpid][event.link.dst.dpid]
        new_dic=self.adjacency
        key_val= [key_val for key_val in new_dic.keys()]
        print("key_val = ",key_val)
        #del new_dic[event.link.src.dpid]
        #k = event.link.src.dpid
        #for key_val in new_dic.keys():
        print( "new_dic = ",new_dic)
        return
