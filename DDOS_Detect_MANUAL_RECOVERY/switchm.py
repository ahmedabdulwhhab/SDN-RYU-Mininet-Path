#################################
"""
 sudo mn -c; sudo mn --controller=remote,ip=127.0.0.1:6633 --mac --switch=ovsk,protocols=OpenFlow13 --topo=linear,3,4

 h4s3 timeout 20s hping3 -S -V -d 120 -w 64 -p 80 --rand-source --flood 10.0.0.1
 
 
 
Start IPERF Server in h3s3
h3s3 iperf -s &
Start the IPERF Client in h1 and connecting to h4
h1s1 iperf -c h3s3
Analyze the results by flows
sudo ovs-ofctl -O OpenFlow13 dump-flows s1
we observe traffic in both directions.

h1 to h4 traffc is very high (in Gbps). This is data traffic. h4 to h1 traffic is very less. This is TCP Acknowledge traffic.

Analyze the results by ports.
sudo ovs-ofctl -O OpenFlow13 dump-ports s1
h1 --------port1, port4--------h4

Forward traffic:

h1 transimits. port1 receives.
port4 transmits, h4 receives.
Acknowlege:

h4 transmits. port4 receives.
port1 transmits. h1 receives.
#### B. Bidirectional Traffic test h1 to h4(sequentially).

Start IPERF Server in h4
h4 iperf -s &
Start the IPERF Client in h1 and connecting to h4
Copy
h1 iperf -c h4 -r 
Start IPERF Server in h4
h4 iperf -s &
Start the IPERF Client in h1 and connecting to h4
h1 iperf -c h4 -d
Its parallel test , both direction h1 to h4 as well h4 to h1 traffic tests started.

#### D. Traffic test from h1 to h4 with Multiple Sessions.

Start IPERF Server in h4
h4 iperf -s &
Start the IPERF Client in h1 and connecting to h4
Copy
h1 iperf -c h4 -P 5


Multiple Parallel calls VOIP calls test
1) Run the IPERF UDP server in h4

mininet>h1s1 iperf --server --udp --len 300 --tos 184 -fk --interval 5 --parallel 4
2) Run the IPERF UDP Client in h1

Copy
mininet>h2s2 iperf -c 10.1.1.4 --udp --len 300 --bandwidth 67000 --dualtest --tradeoff --tos 184 -fk --interval 5 --time 60 --listenport 5002 --parallel 4
#References
"""

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import arp
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types

from ryu.lib.packet import in_proto
from ryu.lib.packet import ipv4
from ryu.lib.packet import icmp
from ryu.lib.packet import tcp
from ryu.lib.packet import udp

FLOW_SERIAL_NO = 0

def get_flow_number():
    global FLOW_SERIAL_NO
    FLOW_SERIAL_NO = FLOW_SERIAL_NO + 1
    return FLOW_SERIAL_NO


class SimpleSwitch13(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch13, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.mitigation = 1
        self.arp_ip_to_port = {}

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        
        flow_serial_no = get_flow_number()

        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions, flow_serial_no)

    def add_flow(self, datapath, priority, match, actions, serial_no, buffer_id=None, idle=0, hard=0):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, cookie=serial_no, buffer_id=buffer_id,
                                    idle_timeout=idle, hard_timeout=hard,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, cookie=serial_no, priority=priority,
                                    idle_timeout=idle, hard_timeout=hard,
                                    match=match, instructions=inst)
            
        datapath.send_msg(mod)

    def block_port(self, datapath, portnumber,src):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        match = parser.OFPMatch(in_port=portnumber,eth_src=src)
        actions = []
        flow_serial_no = get_flow_number()
        
        self.add_flow(datapath, 100, match, actions, flow_serial_no, hard=240)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
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
        self.arp_ip_to_port.setdefault(dpid, {})
        self.arp_ip_to_port[dpid].setdefault(in_port, [])

        # learn a mac address to avoid FLOOD next time.
        self.mac_to_port[dpid][src] = in_port

        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]
        #if ARP Request packet , log the IP and MAC Address from that port
        if eth.ethertype == ether_types.ETH_TYPE_ARP:
            #self.logger.info("Received ARP Packet %s %s %s ", dpid, src, dst)
            a = pkt.get_protocol(arp.arp)
            #print "arp packet ", a
            if a.opcode == arp.ARP_REQUEST or a.opcode == arp.ARP_REPLY:
                if not a.src_ip in self.arp_ip_to_port[dpid][in_port]:
                    self.arp_ip_to_port[dpid][in_port].append(a.src_ip)

        # install a flow to avoid packet_in next time
        if out_port != ofproto.OFPP_FLOOD:

            # check IP Protocol and create a match for IP
            if eth.ethertype == ether_types.ETH_TYPE_IP:
                ip = pkt.get_protocol(ipv4.ipv4)
                srcip = ip.src
                dstip = ip.dst
                protocol = ip.proto

            # check IP Protocol and create a match for IP
            if eth.ethertype == ether_types.ETH_TYPE_IP:
                ip = pkt.get_protocol(ipv4.ipv4)
                srcip = ip.src
                dstip = ip.dst
                protocol = ip.proto

                # if ICMP Protocol
                if protocol == in_proto.IPPROTO_ICMP:
                    t = pkt.get_protocol(icmp.icmp)
                    match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP, eth_dst=dst, eth_src=src,
                                            ipv4_src=srcip, ipv4_dst=dstip,in_port=in_port,
                                            ip_proto=protocol,icmpv4_code=t.code,
                                            icmpv4_type=t.type)

                 #  if TCP Protocol
                elif protocol == in_proto.IPPROTO_TCP:
                    t = pkt.get_protocol(tcp.tcp)
                    match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP, eth_dst=dst, eth_src=src,
                                            ipv4_src=srcip, ipv4_dst=dstip,
                                            ip_proto=protocol,in_port=in_port,
                                            tcp_src=t.src_port, tcp_dst=t.dst_port,)

                #  If UDP Protocol
                elif protocol == in_proto.IPPROTO_UDP:
                    u = pkt.get_protocol(udp.udp)
                    match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP, eth_dst=dst, eth_src=src,
                                            ipv4_src=srcip, ipv4_dst=dstip,
                                            ip_proto=protocol,in_port=in_port,
                                            udp_src=u.src_port, udp_dst=u.dst_port,)
                #print("mitigation")
                if self.mitigation:
                    #print("mitigation_in")
                    if not (srcip in self.arp_ip_to_port[dpid][in_port]):
                        print("attack detected from port ", in_port)
                        print("Block the port ", in_port," at datapath ", datapath.id, " src mac ",src)
                        self.block_port(datapath, in_port,src)
                        #print ip
                        #self.mitigation = 0
                        return

                # verify if we have a valid buffer_id, if yes avoid to send both
                # flow_mod & packet_out
                flow_serial_no = get_flow_number()

                if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                    self.add_flow(datapath, 10, match, actions, flow_serial_no, msg.buffer_id, idle=100, hard=200)
                    return
                else:
                    self.add_flow(datapath, 10, match, actions, flow_serial_no, idle=100, hard=200)
        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)

