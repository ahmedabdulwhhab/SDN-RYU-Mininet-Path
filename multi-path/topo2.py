#!/usr/bin/env python
#multi controller
#clear && ryu-manager ./sdn/ryu-controller/muzixing/ryu/ryu/app/multipath.py  --observe-links --verbose --ofp-tcp-listen-port 6633
#clear && ryu-manager ./sdn/ryu-controller/ah_learn_ryu_00/ryu_multipath.py --observe-links --ofp-tcp-listen-port 6633

from mininet.cli import CLI
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.term import makeTerm

if '__main__' == __name__:
    net = Mininet(controller=RemoteController)

    c0 = net.addController('c0', port=6633)


    s1 = net.addSwitch('s1')
    s2 = net.addSwitch('s2')
    s3 = net.addSwitch('s3')
    s4 = net.addSwitch('s4')
    s5 = net.addSwitch('s5')


    s6 = net.addSwitch('s6')
    s7 = net.addSwitch('s7')
    s8 = net.addSwitch('s8')
    s9 = net.addSwitch('s9')
    s10 = net.addSwitch('s10')

    h1 = net.addHost('h1',mac='00:00:00:00:00:01')
    h2 = net.addHost('h2',mac='00:00:00:00:00:02')
    h3 = net.addHost('h3',mac='00:00:00:00:00:03')
    h4 = net.addHost('h4',mac='00:00:00:00:00:04')


    net.addLink(s1, h1, bw=20.0, delay='10ms', use_htb=True)
    net.addLink(s1, s2, bw=20.0, delay='200ms', use_htb=True)
    net.addLink(s1, s4, bw=20.0, delay='300ms', use_htb=True)
    net.addLink(s1, s5, bw=20.0, delay='400ms', use_htb=True)
    net.addLink(s1, s7, bw=20.0, delay='500ms', use_htb=True)
    net.addLink(s2, s3, bw=20.0, delay='50ms', use_htb=True)
    net.addLink(s4, s3, bw=20.0, delay='150ms', use_htb=True)
    net.addLink(s6, s3, bw=20.0, delay='170ms', use_htb=True)
    net.addLink(s9, s3, bw=20.0, delay='180ms', use_htb=True)
    net.addLink(s5, h3, bw=20.0, delay='1900ms', use_htb=True)
    net.addLink(h2, s3, bw=20.0, delay='210ms', use_htb=True)
    net.addLink(s5, s6, bw=20.0, delay='2400ms', use_htb=True)

    net.addLink(s7, s8, bw=20.0, delay='100ms', use_htb=True)
    net.addLink(s9, s8, bw=20.0, delay='200ms', use_htb=True)

    net.addLink(s7, s10, bw=20.0, delay='100ms', use_htb=True)
    net.addLink(h4, s10, bw=20.0, delay='100ms', use_htb=True)




    net.build()
    c0.start()
    s1.start([c0])
    s2.start([c0])
    s3.start([c0])
    s4.start([c0])
    s5.start([c0])
    s6.start([c0])
    s7.start([c0])
    s8.start([c0])
    s9.start([c0])
    s10.start([c0])


    #net.startTerms()

    CLI(net)

    net.stop()
