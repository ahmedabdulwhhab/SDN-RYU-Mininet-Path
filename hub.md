# SDN-RYU-Mininet-Path <br>
Mix of files<br>
#HUB Application<br>
#Logic<br>
Create a Flow, all Matches with FLOOD Action<br>
<br>
No need of TABLE MISS Entry.<br>
<br>
So, we can simply modify the TABLE MISS Entry action as FLOOD to achieve the HUB Operations.
<br>
#Code changes<br>
In the Switch Features handler, modify the action as FLOOD.<br>
<br>
actions = [parser.OFPActionOutput(port=ofproto.OFPP_FLOOD)]<br>
We will never get Packet_in event , So we can remove those routines.<br>
<br>
Save this file as hub.py<br>
<br>
#Demo<br>
Run Mininet topology<br>
sudo mn --controller=remote,ip=127.0.0.1:7777 --mac --switch=ovsk,protocols=OpenFlow13 --topo=single,4<br>
<br>
Run RYU hub application<br>
ryu-manager hub.py --ofp-tcp-listen-port 7777 <br>
Check the openvswitch flows<br>
sudo ovs-ofctl -O OpenFlow13 dump-flows s1<br>
do pingall from mininet.<br>
<br>
flow table action is flood only<br>
