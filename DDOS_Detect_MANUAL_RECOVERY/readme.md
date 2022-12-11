## DDOS causes buffer of switch to be filled with packets from switches, so after DDOS is finished, the controller is still receving old messages came from switches, while if you use command sudo tcpdump -en -i s2-eth3 which asssuming both switches are connected via port 3, you find there is no flow, while contrller is still receiving from buffer memory.
# topo
sh ./topo.sh


# controller
clear && sudo ryu-manager my_monitor_006_Manual_DDOS_Recovery.py   --ofp-tcp-listen-port 6633


# flood
 h2s2 timeout 20s hping3 -S -V -d 120 -w 64 -p 80 --rand-source --flood 10.0.0.1
 
 # Video
https://youtu.be/zMKsdQTPX3g

<br> In controller <br>
my_monitor_006_Manual_DDOS_Recovery.py              I send flow criterion to only switch that connected to host that cause attack <br>


<br> In controller <br>
my_monitor_007_Manual_DDOS_Recovery.py              I send flow criterion to all switch to block all msgs from this src to this dst  <br>



<br> In controller <br>
my_monitor_008_Manual_DDOS_Recovery.py              I send flow criterion to all switch to block all msgs from this src to this dst  <br>
                                                    display received packet type <br>
                                                    block all messages from this src but giving low prioity to confirm that the rule src=src,dst=dst are blocking 


<br> In controller <br>
my_monitor_009_Manual_DDOS_Recovery.py              I send flow criterion to all switch to block all msgs from this src to this dst  <br>
                                                    display received packet type <br>
                                                    adding idle time=30 sec causes fast recovery than hard time <br>
                                                    also don't wait for IP packet to block , once ethernet packet, add flow entry to block.
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
                    #return-2                                        
                                        #############################    
					
					
					

# in controller 	my_monitor_010_Manual_DDOS_Recovery.py
		after 20 second release variable DDos_occur to be zero

