In this project, we are going to create Dual path topology (Ring TOPO), to avoid looping, we create default path and arp_Table,
The project path on github is <br>
https://github.com/ahmedabdulwhhab/SDN-RYU-Mininet-Path/tree/main/Pre-Configured-Flow_Entry

topo file is  <br>
https://github.com/ahmedabdulwhhab/SDN-RYU-Mininet-Path/blob/main/Pre-Configured-Flow_Entry/topo3_multi-path.py
 <br>
app file is
 <br> https://github.com/ahmedabdulwhhab/SDN-RYU-Mininet-Path/blob/main/Pre-Configured-Flow_Entry/app3_multi-path.py
 <br>
 <br>app file and monitor is
 <br>https://github.com/ahmedabdulwhhab/SDN-RYU-Mininet-Path/blob/main/Pre-Configured-Flow_Entry/app3_multi-path%2Bmonitor.py

 <br> <br>we use also
 <br>- flowmanager to view topo and flowentries
 <br>- ryu.app.ofctl_rest to be able to send curl cmd if needed.

 <br>after running app,
 <br>if you want to change the default path, you can use curl cmd
 <br>curl -X POST -d '{"dpid": 1,"cookie": 1,"cookie_mask": 1,"table_id": 0,"idle_timeout": 3000,"hard_timeout": 3000,"priority": 102,"flags": 1,"match":{"eth_type": 2048,"ip_proto": 1,"ipv4_dst": "10.0.0.2"},"actions":[{"type":"OUTPUT","port": 3}]}' http://localhost:8080/stats/flowentry/add
	 <br><t><t>	<t>			which switch<t>	<t><t><t><t><t><t><t>				opthion timeout<t>	<t>	opthoin timeout<t><t>		priority						<t><t>match criteria	<t>	ICMP<t><t>	which destation			<t>	output port	
	<br>
	<br>
	youtube link is
	<a href="https://youtu.be/7etUx5zl6OA"> To view video about this project, visit this link</a>
