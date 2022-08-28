#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import Controller, OVSKernelSwitch, RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.node import OVSSwitch
from mininet.topo import Topo


class MyTopo(Topo):
    "Simple topology example."

    def emptyNet():
        net = Mininet(controller=RemoteController, switch=OVSKernelSwitch)

        c1 = net.addController('c1', controller=RemoteController, ip="192.168.1.5", port=6634)
        c2 = net.addController('c2', controller=RemoteController, ip="127.0.0.1", port=6633)

        # h1 = net.addHost( 'h1', ip='10.0.0.1', mac='00:00:00:00:00:01' )
        # h2 = net.addHost( 'h2', ip='10.0.0.2', mac='00:00:00:00:00:02' )
        '''
        # For 4 host four switch Topology

        h1 = net.addHost('h1', ip='10.0.0.1')
        h2 = net.addHost('h2', ip='10.0.0.2')
        h3 = net.addHost( 'h3', ip='10.0.0.3' )
        h4 = net.addHost( 'h4', ip='10.0.0.4' )

        s1 = net.addSwitch('s1')
        s2 = net.addSwitch('s2')
        s3 = net.addSwitch('s3')
        s4 = net.addSwitch('s4')

        s1.linkTo( h1 )
        s2.linkTo( h2 )
        s3.linkTo( h3 )
        s4.linkTo( h4 )

        s1.linkTo(s2)
        s2.linkTo(s3)
        s3.linkTo(s4)
        #s4.linkTo(s1)


        net.build()
        c1.start()
        c2.start()
        s1.start([c1, c2])
        s2.start([c1, c2])
        s3.start([c1, c2])
        s4.start([c1, c2])
        '''
        # For 2 host 2 switch Topology

        h1 = net.addHost('h1', ip='10.0.0.1')
        h2 = net.addHost('h2', ip='10.0.0.2')

        s1 = net.addSwitch('s1',cls=OVSSwitch, protocols='OpenFlow13')
        s2 = net.addSwitch('s2',cls=OVSSwitch, protocols='OpenFlow13')

        s1.linkTo(h1)
        s2.linkTo(h2)

        s1.linkTo(s2)

        net.build()
        c1.start()
        c2.start()
        s1.start([c1, c2])
        s2.start([c1, c2])


        net.start()
        net.staticArp()
        CLI(net)
        net.stop()

    if __name__ == '__main__':
        setLogLevel('info')
    emptyNet()


topos = {'mytopo': (lambda: MyTopo())}
