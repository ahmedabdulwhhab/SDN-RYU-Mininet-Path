This project was exracted from A9khan Machine learning.

<br>
https://github.com/a9khan/trafficclassifier/blob/master/NetSoft_project.ipynb
<br>
<br>
https://youtu.be/1tRJu4HnfnA

<br> 
difference between traffic_classifier_python3.py and traffic_classifier_python3_01.py 

<br>
Line 29
<br>traffic_classifier_python3.py
<br>cmd = "sudo ryu run "+proj_location+"simple_monitor_AK.py"
<lLine 31
<br>traffic_classifier_python3_01.py
<br>cmd = "sudo ryu run "+proj_location+"simple_monitor_AK.py    --verbose"


<br>traffic_classifier_python3_01.py
<br> prints received data from simple_monitor
<br> Line 163
<br>  print("      ",fields[0],"\t",fields[1],"\t\t",fields[2],"\t",fields[3],"\t",fields[4],"\t",fields[5],"\t\t",fields[6],"\t",fields[7])           #Ahmed Abdulwhhab


<br> collected data are
<br>Forward Packets<br>Forward Bytes<br>Delta Forward Packets<br>Delta Forward Bytes<br>Forward Instantaneous Packets per Second<br>Forward Average Packets per second<br>Forward Instantaneous Bytes per Second<br>Forward Average Bytes per second<br>Reverse Packets<br>Reverse Bytes<br>Delta Reverse Packets<br>Delta Reverse Bytes<br>DeltaReverse Instantaneous Packets per Second<br>Reverse Average Packets per second<br>Reverse Instantaneous Bytes per Second<br>Reverse Average Bytes per second<br>Traffic Type
<br>forward_avg_pps = packets/float(curr_time-self.time_start)
<br>forward_delta_packets = packets - forward_packets
<br>forward_packets = packets
<br>forward_avg_pps = packets/float(curr_time-time_start)
<br>forward_inst_pps = self.forward_delta_packets/float(curr_time-self.forward_last_time)
        
<br>forward_delta_bytes = bytes - self.forward_bytes
<br>forward_bytes = bytes
<br>forward_avg_bps = bytes/float(curr_time-self.time_start)
<br>forward_inst_bps = self.forward_delta_bytes/float(curr_time-self.forward_last_time)
<br>forward_last_time = curr_time

<br> a9khan project is based on monitor of     @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
<br> FlowStatsReplay
<br> important data is preceeded by word data
<br> another issue, you can depend on     @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
<br> as per simple_monitor_AK_01 , but you have to modify the code by your self.
<br> to view each port no. of packets
<br>                self.logger.info('%016x %8x %8d %8d %8d %8d %8d %8d %12d %12d',
                             ev.msg.datapath.id, stat.port_no,
                             stat.rx_packets, stat.rx_bytes, stat.rx_errors,
                             stat.tx_packets, stat.tx_bytes, stat.tx_errors,
                             stat.duration_sec , stat.duration_nsec)
