# SDN-RYU-Mininet-Path
Mix of files
#HUB Application
#Logic
Create a Flow, all Matches with FLOOD Action

No need of TABLE MISS Entry.

So, we can simply modify the TABLE MISS Entry action as FLOOD to achieve the HUB Operations.

#Code changes
In the Switch Features handler, modify the action as FLOOD.

actions = [parser.OFPActionOutput(port=ofproto.OFPP_FLOOD)]
We will never get Packet_in event , So we can remove those routines.

Save this file as hub.py

#Demo
Run Mininet topology
sudo mn --controller=remote,ip=127.0.0.1 --mac --switch=ovsk,protocols=OpenFlow13 --topo=single,4

Run RYU hub application
ryu-manager hub.py
Check the openvswitch flows
sudo ovs-ofctl -O OpenFlow13 dump-flows s1
do pingall from mininet.
<br>
flow table action is flood only
