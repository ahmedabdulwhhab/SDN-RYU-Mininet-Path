#https://github.com/palakbhonsle/SDN-Simulation-using-RYU/blob/master/l4_switch1.py


#sudo ryu-manager /home/ubuntu/sdn/projects/a9khan/multipath_net_classifier_mod_path/app5_multi-path+monitor.py  /home/ubuntu/sdn/sources/flowmanager/flowmanager.py ryu.app.ofctl_rest   --observe-links --ofp-tcp-listen-port 6644


#sudo mn -c && sudo python3 /home/ubuntu/sdn/projects/packet_analyzer/l4Switch/topo.py
#curl -X POST -d '{"dpid": 1,"cookie": 1,"cookie_mask": 1,"table_id": 0,"idle_timeout": 3000,"hard_timeout": 3000,"priority": 2,"flags": 1,"match":{"eth_type": 2048,"ip_proto": 1,"ipv4_dst": "10.0.0.2"},"actions":[{"type":"OUTPUT","port": 2}]}' http://localhost:8080/stats/flowentry/add
#curl -X POST -d '{"dpid": 1,"cookie": 1,"cookie_mask": 1,"table_id": 0,"idle_timeout": 3000,"hard_timeout": 3000,"priority": 2,"flags": 1,"match":{"in_port": 3,"dl_dst": "00:00:00:00:00:01","dl_src": "00:00:00:00:00:02"},"actions":[{"type":"OUTPUT","port": 1}]}' http://localhost:8081/stats/flowentry/add

#curl -X POST -d '{"dpid": 3,"cookie": 1,"cookie_mask": 1,"table_id": 0,"idle_timeout": 3000,"hard_timeout": 3000,"priority": 2,"flags": 1,"match":{"in_port": 1,"dl_dst": "00:00:00:00:00:02","dl_src": "00:00:00:00:00:01"},"actions":[{"type":"OUTPUT","port": 2}]}' http://localhost:8081/stats/flowentry/add
#curl -X POST -d '{"dpid": 3,"cookie": 1,"cookie_mask": 1,"table_id": 0,"idle_timeout": 3000,"hard_timeout": 3000,"priority": 2,"flags": 1,"match":{"in_port": 2,"dl_dst": "00:00:00:00:00:01","dl_src": "00:00:00:00:00:02"},"actions":[{"type":"OUTPUT","port": 1}]}' http://localhost:8081/stats/flowentry/add

#curl -X POST -d '{"dpid": 2,"cookie": 1,"cookie_mask": 1,"table_id": 0,"idle_timeout": 3000,"hard_timeout": 3000,"priority": 2,"flags": 1,"match":{"in_port": 2,"dl_dst": "00:00:00:00:00:02","dl_src": "00:00:00:00:00:01"},"actions":[{"type":"OUTPUT","port": 3}]}' http://localhost:8081/stats/flowentry/add
#curl -X POST -d '{"dpid": 2,"cookie": 1,"cookie_mask": 1,"table_id": 0,"idle_timeout": 3000,"hard_timeout": 3000,"priority": 2,"flags": 1,"match":{"in_port": 3,"dl_dst": "00:00:00:00:00:01","dl_src": "00:00:00:00:00:02"},"actions":[{"type":"OUTPUT","port": 2}]}' http://localhost:8081/stats/flowentry/add


from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.ofproto import ether
from ryu.ofproto import inet
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import arp
from ryu.lib.packet import ipv4
from ryu.lib.packet import tcp
from ryu.lib.packet import udp
# you may import more libs here, but the above libs should be enough

###############
from operator import attrgetter
from datetime import datetime
from ryu.app import simple_switch_13
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub
##################


class Switch(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    
    """
        Constructor:
        You can define some globally used variables inside the class
    """
    def __init__(self, *args, **kwargs):
        super(Switch, self).__init__(*args, **kwargs)
        # arp table: for searching
        self.arp_table={}
        self.arp_table["10.0.0.1"] = "00:00:00:00:00:01"
        self.arp_table["10.0.0.2"] = "00:00:00:00:00:02"
        self.arp_table["10.0.0.3"] = "00:00:00:00:00:03"
        self.arp_table["10.0.0.4"] = "00:00:00:00:00:04"
        self.datapaths = {}
        self.monitor_thread = hub.spawn(self._monitor)
        self.fields = {'time':'','datapath':'','in-port':'','eth_src':'','eth_dst':'','out-port':'','total_packets':0,'total_bytes':0}
    """
        Hand-shake event call back method
        This is the very initial method where the switch hand shake with the controller
        It checks whether both are using the same protocol version: OpenFlow 1.3 in this case
        Therefore in this method, we can setup some static rules.
    """
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        
        # Insert Static rule
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

        # Installing static rules to process TCP/UDP and ICMP and ACL
        dpid = datapath.id  # classifying the switch ID
        print("switch is connected at datapath.id ", dpid)
        print("inet.IPPROTO_ICMP ", inet.IPPROTO_ICMP)
        print("inet.IPPROTO_TCP ", inet.IPPROTO_TCP)        
        print("inet.IPPROTO_UDP ", inet.IPPROTO_UDP)
        if dpid == 1: # switch S1
            ### implement ICMP Forwarding
            #tcp_match = parser.OFPMatch(in_port=in_port, eth_dst=dst, ip_proto=6)
            #add_flowentry_rules(datapath, ip_proto,ipv4_dst   ipv4_src = None, priority = 1, fwd_port = None,inport=None):
            self.add_flowentry_rules(datapath, inet.IPPROTO_ICMP, '10.0.0.1','10.0.0.2', 10, 1,2)#same dst same fwport
            self.add_flowentry_rules(datapath, inet.IPPROTO_ICMP, '10.0.0.1','10.0.0.3', 10, 1,2)#same dst same fwport
            self.add_flowentry_rules(datapath, inet.IPPROTO_ICMP, '10.0.0.1','10.0.0.4', 10, 1,2)#same dst same fwport
            
            self.add_flowentry_rules(datapath, inet.IPPROTO_ICMP, '10.0.0.3','10.0.0.1', 10, 3,1)
            self.add_flowentry_rules(datapath, inet.IPPROTO_ICMP, '10.0.0.2','10.0.0.1', 10, 3,1)
            self.add_flowentry_rules(datapath, inet.IPPROTO_ICMP, '10.0.0.4','10.0.0.1', 10, 3,1)
            
            self.add_flowentry_rules(datapath, inet.IPPROTO_ICMP, '10.0.0.4','10.0.0.2', 10, 3,2)
            self.add_flowentry_rules(datapath, inet.IPPROTO_ICMP, '10.0.0.3','10.0.0.2', 10, 3,2)
            self.add_flowentry_rules(datapath, inet.IPPROTO_ICMP, '10.0.0.4','10.0.0.3', 10, 3,2)
        elif dpid == 2: # switch S2  
            ### Implement ICMP Forwarding
            #add_flowentry_rules(datapath, ip_proto,ipv4_dst   ipv4_src = None, priority = 1, fwd_port = None,inport=None):
            self.add_flowentry_rules(datapath, inet.IPPROTO_ICMP, '10.0.0.2','10.0.0.1', 10, 1,3)#same dst same fwport
            self.add_flowentry_rules(datapath, inet.IPPROTO_ICMP, '10.0.0.2','10.0.0.3', 10, 1,3)#same dst same fwport
            self.add_flowentry_rules(datapath, inet.IPPROTO_ICMP, '10.0.0.2','10.0.0.4', 10, 1,3)#same dst same fwport
            
            self.add_flowentry_rules(datapath, inet.IPPROTO_ICMP, '10.0.0.3','10.0.0.2', 10, 2,1)
            self.add_flowentry_rules(datapath, inet.IPPROTO_ICMP, '10.0.0.1','10.0.0.2', 10, 2,1)
            self.add_flowentry_rules(datapath, inet.IPPROTO_ICMP, '10.0.0.4','10.0.0.2', 10, 2,1)
            
            self.add_flowentry_rules(datapath, inet.IPPROTO_ICMP, '10.0.0.4','10.0.0.3', 10, 2,3)
            self.add_flowentry_rules(datapath, inet.IPPROTO_ICMP, '10.0.0.1','10.0.0.3', 10, 2,3)
            self.add_flowentry_rules(datapath, inet.IPPROTO_ICMP, '10.0.0.1','10.0.0.4', 10, 2,3)

        elif dpid == 3: # switch S3 
            ### Implement ICMP Forwarding
            #add_flowentry_rules(datapath, ip_proto,               ipv4_dst   ipv4_src = None, priority = 1, fwd_port = None,inport=None):
            self.add_flowentry_rules(datapath, inet.IPPROTO_ICMP, '10.0.0.3','10.0.0.1', 10, 1,3)#same dst same fwport
            self.add_flowentry_rules(datapath, inet.IPPROTO_ICMP, '10.0.0.3','10.0.0.2', 10, 1,3)#same dst same fwport
            self.add_flowentry_rules(datapath, inet.IPPROTO_ICMP, '10.0.0.3','10.0.0.4', 10, 1,3)#same dst same fwport
            
            self.add_flowentry_rules(datapath, inet.IPPROTO_ICMP, '10.0.0.2','10.0.0.3', 10, 2,1)
            self.add_flowentry_rules(datapath, inet.IPPROTO_ICMP, '10.0.0.1','10.0.0.3', 10, 2,1)
            self.add_flowentry_rules(datapath, inet.IPPROTO_ICMP, '10.0.0.4','10.0.0.3', 10, 2,1)
            
            self.add_flowentry_rules(datapath, inet.IPPROTO_ICMP, '10.0.0.2','10.0.0.4', 10, 2,3)
            self.add_flowentry_rules(datapath, inet.IPPROTO_ICMP, '10.0.0.1','10.0.0.4', 10, 2,3)
            self.add_flowentry_rules(datapath, inet.IPPROTO_ICMP, '10.0.0.2','10.0.0.1', 10, 2,3)
        elif dpid == 4: # switch S4           
            ### Implement ICMP Forwarding
            self.add_flowentry_rules(datapath, inet.IPPROTO_ICMP, '10.0.0.4','10.0.0.1', 10, 1,3)#same dst same fwport
            self.add_flowentry_rules(datapath, inet.IPPROTO_ICMP, '10.0.0.4','10.0.0.3', 10, 1,3)#same dst same fwport
            self.add_flowentry_rules(datapath, inet.IPPROTO_ICMP, '10.0.0.4','10.0.0.2', 10, 1,3)#same dst same fwport
            
            self.add_flowentry_rules(datapath, inet.IPPROTO_ICMP, '10.0.0.3','10.0.0.4', 10, 2,1)
            self.add_flowentry_rules(datapath, inet.IPPROTO_ICMP, '10.0.0.1','10.0.0.4', 10, 2,1)
            self.add_flowentry_rules(datapath, inet.IPPROTO_ICMP, '10.0.0.2','10.0.0.4', 10, 2,1)
            
            self.add_flowentry_rules(datapath, inet.IPPROTO_ICMP, '10.0.0.3','10.0.0.1', 10, 2,3)
            self.add_flowentry_rules(datapath, inet.IPPROTO_ICMP, '10.0.0.2','10.0.0.1', 10, 2,3)
            self.add_flowentry_rules(datapath, inet.IPPROTO_ICMP, '10.0.0.3','10.0.0.2', 10, 2,3)



        else:
            print ("wrong switch")
    

    """ 
        Call back method for PacketIn Message
        This is the call back method when a PacketIn Msg is sent
        from a switch to the controller
        It handles L3 classification in this function:
    """ 
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

        # process IP
        if ethertype == ether.ETH_TYPE_IP:
            self.handle_ip(datapath, in_port, pkt)
            return

    # Member methods you can call to install TCP/UDP/ICMP fwding rules
    def add_flowentry_rules(self, datapath, ip_proto, ipv4_dst = None,ipv4_src = None, priority = 1, fwd_port = None,inport=None):
        parser = datapath.ofproto_parser
        actions = [parser.OFPActionOutput(fwd_port)]
        match = parser.OFPMatch(eth_type = ether.ETH_TYPE_IP,
                                ip_proto = ip_proto,
                                ipv4_dst = ipv4_dst,
                                ipv4_src = ipv4_src,
                                in_port=inport)
        self.add_flow(datapath, priority, match, actions)

    # Member methods you can call to install general rules
    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]

        mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                match=match, instructions=inst)
        datapath.send_msg(mod)

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

    """
        Methods to handle TCP/IP. In this implementation the controller
        generate the TCP RST for connections between h1 and h3.
        In switch_features_handler()put a static rule to fwd 
        those packets to the controller, and in handle_ip()  
        generate and return the TCP RST with PacketOut Message
    """
    def handle_ip(self, datapath, in_port, pkt):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        print(" inside handle_ip , pkt ",pkt)

        ipv4_pkt = pkt.get_protocol(ipv4.ipv4) # parse out the IPv4 pkt
        #print(" inside handle_ip , ipv4_pkt ",ipv4_pkt)

        if datapath.id == 1 and ipv4_pkt.proto == inet.IPPROTO_TCP:
            tcp_pkt = pkt.get_protocol(tcp.tcp) # parser out the TCP pkt
            eth_pkt = pkt.get_protocol(ethernet.ethernet)
            #if (tcp_pkt.bits) % 4 == 2:

            ### generate the TCP packet with the RST flag set to 1
            ### packet generation is similar to ARP,
            ### but you need to generate ethernet->ip->tcp and serialize it
            
            #tcp_hd = tcp.tcp(src_port=tcp_pkt.src_port, dst_port=tcp_pkt.dst_port, seq=tcp_pkt.seq, ack=tcp_pkt.ack, offset=tcp_pkt.offset, bits=tcp_pkt.bits, window_size=tcp_pkt.window_size, csum=tcp_pkt.csum, urgent=tcp_pkt.urgent, option=tcp_pkt.option)
            # ip_hd = ipv4.ipv4(dst= ipv4_pkt.src, src= ipv4_pkt.dst, proto=ipv4_pkt.proto)
            # ether_hd = ethernet.ethernet(ethertype = ether.ETH_TYPE_IP, dst = eth_pkt.src, src = eth_pkt.dst)
            
           
            ##src_port=1, dst_port=1, seq=0, ack=0, offset=0, bits=0, window_size=0, csum=0, urgent=0, option=None
            #tcp_hd = tcp.tcp(ack=tcp_pkt.ack,seq=tcp_pkt.seq, src_port = tcp_pkt.src_port, dst_port = tcp_pkt.dst_port, bits=tcp_pkt.bits, csum=tcp_pkt.csum, offset=tcp_pkt.offset,option=tcp_pkt.option)
            tcp_hd = tcp.tcp(src_port=tcp_pkt.src_port, dst_port=tcp_pkt.dst_port, seq=tcp_pkt.seq, ack=tcp_pkt.ack, offset=tcp_pkt.offset, bits=tcp_pkt.bits, window_size=tcp_pkt.window_size, csum=tcp_pkt.csum, urgent=tcp_pkt.urgent, option=tcp_pkt.option)
            ip_hd = ipv4.ipv4(dst= ipv4_pkt.dst, src= ipv4_pkt.src, proto=ipv4_pkt.proto)
            ether_hd = ethernet.ethernet(ethertype = ether.ETH_TYPE_IP, src = eth_pkt.src, dst = eth_pkt.dst)            
            out_port=in_port
            if( eth_pkt.src=="00:00:00:00:00:03" and eth_pkt.dst=="00:00:00:00:00:01"):  
                out_port=1
                # ether_hd  ethernet(dst='00:00:00:00:00:01',ethertype=2048,src='00:00:00:00:00:03')
            elif( eth_pkt.src=="00:00:00:00:00:01" and eth_pkt.dst=="00:00:00:00:00:03"):
                out_port=2
            
            tcp_rst_ack = packet.Packet()
            tcp_rst_ack.add_protocol(ether_hd)
            tcp_rst_ack.add_protocol(ip_hd)
            tcp_rst_ack.add_protocol(tcp_hd)
            if(len(pkt) >3):
                #if payload_data
                payload = pkt.protocols[::-1][0]    
                tcp_rst_ack.add_protocol(bytearray (payload))
                print(" payload ", payload)
            tcp_rst_ack.serialize()

            
            # send the Packet Out mst to back to the host who is initilaizing the ARP
            #actions = [parser.OFPActionOutput(in_port)];
            actions = [parser.OFPActionOutput(out_port)];
            out = parser.OFPPacketOut(datapath, ofproto.OFP_NO_BUFFER, 
                                      ofproto.OFPP_CONTROLLER, actions,
                                      tcp_rst_ack.data)
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
        self.logger.info('time      datapath    dpid    '
                         'in-port  ipv4_src     ipv4_dst    '
                         'out-port total_packets  total_bytes')

        self.logger.info('---------------- '
                         '-------- ----------------- '
                         '-------- -------- --------')
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
   
