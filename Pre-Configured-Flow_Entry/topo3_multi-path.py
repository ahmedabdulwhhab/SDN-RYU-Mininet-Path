#clear && sudo ryu-manager /home/ubuntu/sdn/projects/multi-path/app3.py  /home/ubuntu/sdn/sources/flowmanager/flowmanager.py   --observe-links --ofp-tcp-listen-port 6633

#https://github.com/palakbhonsle/SDN-Simulation-using-RYU/blob/master/custom1%20(1).py
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info


def custoNet():

    net = Mininet()
    
    info('***Adding Ryu Controller \n')
    ryuCtrl = net.addController(name = 'ryuCtrl', controller = RemoteController, ip = '127.0.0.1')

    info('***Adding Hosts \n')
    H1 = net.addHost('h1', ip = '10.0.0.1', mac = '00:00:00:00:00:01')
    H2 = net.addHost('h2', ip = '10.0.0.2', mac = '00:00:00:00:00:02')
    H3 = net.addHost('h3', ip = '10.0.0.3', mac = '00:00:00:00:00:03')
    H4 = net.addHost('h4', ip = '10.0.0.4', mac = '00:00:00:00:00:04')

    info('***Adding Switch \n')
    S1 = net.addSwitch('s1')
    S2 = net.addSwitch('s2')
    S3 = net.addSwitch('s3')
    S4 = net.addSwitch('s4')

    info('***Adding Links \n')
    net.addLink(H1,S1)
    net.addLink(H2,S2)
    net.addLink(H3,S3)
    net.addLink(H4,S4)
    net.addLink(S1,S2)
    net.addLink(S2,S3)
    net.addLink(S3,S4)
    net.addLink(S4,S1)
  
    info('***Starting Network \n')
    net.start()
  
    info('***Running CLI \n')
    CLI(net)

    info('***Stopping Network \n')
    net.stop()

if __name__=='__main__':
    setLogLevel('info')
    custoNet()