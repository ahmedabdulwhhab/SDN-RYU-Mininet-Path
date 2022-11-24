# topo
sh ./topo.sh


# controller
clear && sudo ryu-manager my_monitor_006_Manual_DDOS_Recovery.py   --ofp-tcp-listen-port 6633


# flood
 h2s2 timeout 20s hping3 -S -V -d 120 -w 64 -p 80 --rand-source --flood 10.0.0.1
 
 # Video
https://youtu.be/zMKsdQTPX3g

<br> In controller <br>
my_monitor_006_Manual_DDOS_Recovery.py              i send flow criterion to only switch that connected to host that cause attack <br>


<br> In controller <br>
my_monitor_007_Manual_DDOS_Recovery.py              i send flow criterion to all switch to block all msgs from this src to this dst  <br>
