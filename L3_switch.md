# SDN-RYU-Mininet-Path <br>
Mix of files <br>
Switch Application With L3 Match <br>
#Logic <br>
simple_switch_13 application as a base application and switch learning process is same <br>

But Flow will be based on Layer3 Match (src ip and destination ip) instead of src_mac and dst_mac <br>

#Code changes <br>
include the IP library <br>
        <b>from ryu.lib.packet import ipv4 </b><br>
Populate the Match based on IP. <br>
Check the packet is IP Packet, then decode the srcip and dstip from the packet header <br>
Populate the Match based on srcip and dstip. <br>

::::::::# install a flow to avoid packet_in next time<br>
::::::::if out_port != ofproto.OFPP_FLOOD:<br>

:::::::::::# check IP Protocol and create a match for IP<br>
:::::::::::if eth.ethertype == ether_types.ETH_TYPE_IP:<br>
::::::::::::::ip = pkt.get_protocol(ipv4.ipv4)<br>
::::::::::::::srcip = ip.src<br>
::::::::::::::dstip = ip.dst<br>
::::::::::::::match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP,
                                        ipv4_src=srcip,
                                        ipv4_dst=dstip
                                        )<br>
::::::::::::::# verify if we have a valid buffer_id, if yes avoid to send both<br>
::::::::::::::# flow_mod & packet_out<br>
::::::::::::::if msg.buffer_id != ofproto.OFP_NO_BUFFER:<br>
::::::::::::::::::self.add_flow(datapath, 1, match, actions, msg.buffer_id)<br>
::::::::::::::::::return<br>
::::::::::::::else:<br>
::::::::::::::::::self.add_flow(datapath, 1, match, actions)<br>



Demo <br>
Run Mininet topology<br>
sudo mn --controller=remote,ip=127.0.0.1 --mac --switch=ovsk,protocols=OpenFlow13 --topo=single,4<br>
<br>
Run RYU hub application<br>
ryu-manager L3_switch.py<br>
do pingall from mininet. <br>
<br>
Check the openvswitch flows<br>


sudo ovs-ofctl -O OpenFlow13 dump-flows s1
