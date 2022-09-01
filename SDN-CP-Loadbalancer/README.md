# Elasticon:

Ref - ElastiCon: An Elastic Distributed SDN Controller, Advait Dixit, Fang Hao, Sarit Mukherjee, T. V. Lakshman, Ramana Rao Kompella.

Present day networking has revolutionised itself by
providing a centralized view of the entire network, making it
easier to manage and control. Software Defined Networking is
an emerging paradigm for implementing centralized control in
modern networking technologies like data centers where the data
is handled by a large amount of switches. Handling this large
data dynamically is a challenge in modern day networking since
performance is a vital criteria for every client. The key limitation
of present day network architecture is the static configuration
between the switch and controller which results in an uneven
distribution of the load in case of sudden dynamic shift in the
load .
To address this problem, ElastiCon, an elastic distributed
controller architecture is proposed in which the controller pool is
dynamically grown or shrunk according to traffic conditions to
address the load imbalance situations in the network. Depending
upon the load, Elasticon automatically balances the load among
the controllers thus ensuring normal performance even during
peak traffic. We implement a database to determine the load on
the controllers and also a switch migration protocol to transfer
the switch to another controller for load balancing.


Code:
-------------------------------------------------
controller_1.py and controller_2.py: RYU Controller app with Elasticon Protocol.
load_balancer.py: Load Balancer App for DB access and migration decision making.
multi_ctlr_topo.py: Topology file for Mininet.


Steps to run:
--------------------------------------------------
1) to use mongod, you have to create folder named as data then inside it create dp then use --dbpath option to run it as below.
2) Start mongodb using: sudo mongod --dbpath='/home/ubuntu/sdn/projects/sdn-cp-loadbalancer/data/dp/'
3) Launch Controller 1 using:
ryu-manager --verbose --ofp-listen-host <IP address of controller 1> controller_1.py
<br> ryu-manager --verbose --ofp-tcp-listen-port 6634 controller_1.py
3) Launch Controller 2 using:
ryu-manager --verbose --ofp-listen-host <IP address of controller 2> controller_2.py
<br> ryu-manager --verbose --ofp-tcp-listen-port 6633 controller_2.py
4) Update IP addresses of the two remote controllers at net.addController() in mininet topology file.
5) Launch mininet for remote controllers with the topology file:
sudo mn --custom multi_ctlr_topo.py --controller=remote --topo mytopo


Steps to verify:
---------------------------------------------------
1) Open a python shell and connect to the db using
   
   client = MongoClient('localhost', 27017)      
   db = client.elastiCon     
   controllers = db.controllers   
   flags = db.flags  
   gen_id = db.gen_id  
   cmf = db.cmf   

2) Monitor the Packet counts at both controllers using
   controllers.find_one({'id':'1'})  
   controllers.find_one({'id':'2'})   

3) Initiate a ping in the mininet
   
   mininet> h1 ping h2 -i 3   
   
   Here we use -i 3 so that packet counts can be clearly monitored.

4) Observe that, when the count reaches 150, the switch is migrated and the controller ceases to receive further packetINs. Instead, the other controller's packetIN resets and starts to increment.

5) Between multiple runs ensure to drop the documents of the db using:

   controllers.drop()  
   flags.drop()   
   gen_id.drop()  
   cmf.drop()    




