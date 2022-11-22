# topo
sh ./topo.sh


#controller
clear && sudo ryu-manager manual_DDos_Recovery.py   --ofp-tcp-listen-port 6633


# flood
 h2s2 timeout 20s hping3 -S -V -d 120 -w 64 -p 80 --rand-source --flood 10.0.0.1
 
 # https://youtu.be/zMKsdQTPX3g

