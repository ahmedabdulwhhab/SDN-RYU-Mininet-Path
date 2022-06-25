# https://github.com/al13mi/multipath-1/blob/master/ryu_multipath.py
# sudo rm ./sdn/ryu-controller/ah_learn_ryu_00/ryu_multipath.py && sudo vim  ./sdn/ryu-controller/ah_learn_ryu_00/ryu_multipath.py
# clear && ryu-manager ./sdn/ryu-controller/ah_learn_ryu_00/ryu_multipath.py --observe-links --ofp-tcp-listen-port 6633
#clear && sudo ryu-manager ./sdn/ryu-controller/ah_learn_ryu_00/ryu_multipath.py ./sdn/ryu-controller/flowmanager/flowmanager.py  --observe-links --ofp-tcp-listen-port 6633
#clear && sudo ryu-manager multi_path_controller.py ../flowmanager/flowmanager.py  --observe-links --ofp-tcp-listen-port 6633
#http://192.168.1.8:8080/home/topology.html
#sudo ovs-ofctl -O openflow13 dump-flows s1
#sudo ovs-ofctl -O openflow13 dump-groups s1

from ryu.base import app_manager
from ryu.controller import mac_to_port
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.mac import haddr_to_bin
from ryu.lib.packet import packet
from ryu.lib.packet import arp
from ryu.lib.packet import ethernet
from ryu.lib.packet import ipv4
from ryu.lib.packet import ipv6
from ryu.lib.packet import ether_types
from ryu.lib import mac, ip
from ryu.topology.api import get_switch, get_link
from ryu.app.wsgi import ControllerBase
from ryu.topology import event

from collections import defaultdict
from operator import itemgetter

import os
import random
import time

# Cisco Reference bandwidth = 1 Gbps
REFERENCE_BW = 10000000

DEFAULT_BW = 10000000

MAX_PATHS = float('Inf')

idle_time=10

class ProjectController(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(ProjectController, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.topology_api_app = self
        self.datapath_list = {}
        self.arp_table = {}
        self.switches = []
        self.hosts = {}
        self.multipath_group_ids = {}
        self.group_ids = []
        self.adjacency = defaultdict(dict)
        self.bandwidths = defaultdict(lambda: defaultdict(lambda: DEFAULT_BW))
        self.en_clear_flow_entry = False
