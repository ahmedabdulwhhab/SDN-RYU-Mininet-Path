#!/usr/bin/python
# sudo git clone https://github.com/intrig-unicamp/mininet-wifi
# cd mininet-wifi/
#sudo util/install.sh -Wlnfv
#/usr/bin/python3 -m pip install --upgrade pip


# sudo mn -c && clear && sudo python3 /home/ubuntu/sdn/projects/wifi/topo_wifi_1.py
#sudo ovs-vsctl set Bridge s1 protocols=OpenFlow13
#sudo ryu-manager /home/ubuntu/sdn/sources/flowmanager/flowmanager.py /home/ubuntu/sdn/projects/wifi/app1.py --observe-links --ofp-tcp-listen-port 6634

from mininet.node import Host, OVSKernelSwitch
from mininet.log import setLogLevel, info
from mn_wifi.net import Mininet_wifi
from mn_wifi.node import Station, OVSKernelAP
#from mn_wifi.cli import CLI_wifi
from mininet.cli import CLI
from mn_wifi.link import wmediumd
from mn_wifi.wmediumdConnector import interference
from subprocess import call


from mininet.node import OVSSwitch, Controller, RemoteController
def myNetwork():



    net = Mininet_wifi(topo=None,
                       build=False,
                       link=wmediumd,
                       wmediumd_mode=interference,
                       ipBase='10.0.0.0/8',
                       controller=RemoteController)
    c0 = net.addController('c0', port=6634)
    info( '*** Adding controller\n' )
    info( '*** Add switches/APs\n')
    


    ap1 = net.addAccessPoint('ap1', cls=OVSKernelAP, ssid='ap1-ssid',
                             channel='1', mode='g', position='126.0,276.0,0', failMode='standalone')
                               
    #s2 = net.addSwitch('s2', cls=OVSKernelSwitch, failMode='standalone')
    s2 = net.addSwitch('s2', dpid='0000000000000002',cls=OVSSwitch, protocols='OpenFlow13')
    #s3 = net.addSwitch('s3', cls=OVSKernelSwitch, failMode='standalone')
    s3 = net.addSwitch('s3', dpid='0000000000000003',cls=OVSSwitch, protocols='OpenFlow13')
    #s1 = net.addSwitch('s1', cls=OVSKernelSwitch, failMode='standalone')
    s1 = net.addSwitch('s1', dpid='0000000000000001',cls=OVSSwitch, protocols='OpenFlow13')

    info( '*** Add hosts/stations\n')
    h3 = net.addHost('h3', cls=Host, ip='10.0.0.3', defaultRoute=None)
    h5 = net.addHost('h5', cls=Host, ip='10.0.0.5', defaultRoute=None)
    sta1 = net.addStation('sta1', ip='10.0.0.101',
                           position='44.0,447.0,0')
    h4 = net.addHost('h4', cls=Host, ip='10.0.0.4', defaultRoute=None)
    h1 = net.addHost('h1', cls=Host, ip='10.0.0.1', defaultRoute=None)
    h2 = net.addHost('h2', cls=Host, ip='10.0.0.2', defaultRoute=None)
    sta2 = net.addStation('sta2', ip='10.0.0.102',
                           position='153.0,447.0,0')

    info("*** Configuring Propagation Model\n")
    net.setPropagationModel(model="logDistance", exp=3)

    info("*** Configuring wifi nodes\n")
    net.configureWifiNodes()

    info( '*** Add links\n')
    net.addLink(ap1, s1)
    net.addLink(h1, s1)
    net.addLink(h2, s2)
    net.addLink(h3, s2)
    net.addLink(s1, s2)
    net.addLink(h4, s3)
    net.addLink(h5, s3)
    net.addLink(s3, s2)

    net.plotGraph(max_x=1000, max_y=1000)

    info( '*** Starting network\n')
    net.build()
    info( '*** Starting controllers\n')
    c0.start()
    ap1.start([c0])
    #for controller in net.controllers:
    #    controller.start()

    info( '*** Starting switches/APs\n')
    net.get('ap1').start([c0])
    net.get('s2').start([c0])
    net.get('s3').start([c0])
    net.get('s1').start([c0])

    info( '*** Post configure nodes\n')

    CLI(net)
    net.stop()
    #print ("*** Running CLI")
    #CLI( net )

    #print ("*** Stopping network")
    #net.stop()


if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()
    print("You are welcom")
    """
    print("configuring Propagation Model\n")
    net.setPropagationModel(model="logDistance", exp=3)

    info("*** Configuring wifi nodes\n")
    net.configureWifiNodes()

    info( '*** Add links\n')
    net.addLink(ap1, s1)
    net.addLink(h1, s1)
    net.addLink(h2, s2)
    net.addLink(h3, s2)
    net.addLink(s1, s2)
    net.addLink(h4, s3)
    net.addLink(h5, s3)
    net.addLink(s3, s2)
    """
