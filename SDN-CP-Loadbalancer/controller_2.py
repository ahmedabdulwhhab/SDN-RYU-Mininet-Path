# Copyright (C) 2011 Nippon Telegraph and Telephone Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.


#ryu-manager --verbose --ofp-tcp-listen-port 6633 controller_2.py

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import HANDSHAKE_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
from ryu.controller import dpset
from ryu.lib.packet import icmp

import random
import load_balancer
import pickle
import time


class SimpleSwitch13(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch13, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.gen_id = 2
        self.role_string_list = ['nochange', 'equal', 'master', 'slave', 'unknown']
        self.ctlr_id = 2
        load_balancer.add_new_controller(self.ctlr_id)
        self.flag_mis_updated = False
        self.mip_status = {'status': 'False', 'dpid': '0', 'datapath': ''}
        self.status_mip_updated = False
        self.start_time, self.stop_time = 0, 0
        self.ActiveMigrationProcess = False

        # Loaded controller Variables
        self.flag_mip_updated = False
        self.mig_end_status = True
        self.mip_flag_status = {'status': 'False', 'dpid': '0', 'datapath': ''}

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # install table-miss flow entry
        #
        # We specify NO BUFFER to max_len of the output action due to
        # OVS bug. At this moment, if we specify a lesser number, e.g.,
        # 128, OVS will send Packet-In with invalid buffer_id and
        # truncated packet data. In that case, we cannot output packets
        # correctly.  The bug has been fixed in OVS v2.1.0.
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst)
        datapath.send_msg(mod)

    def send_barrier_request(self, datapath):
        ofp_parser = datapath.ofproto_parser

        req = ofp_parser.OFPBarrierRequest(datapath)
        datapath.send_msg(req)
        print('Barrier Request Sent')

    @set_ev_cls(ofp_event.EventOFPBarrierReply, MAIN_DISPATCHER)
    def barrier_reply_handler(self, ev):
        self.logger.debug('OFPBarrierReply received')
        self.logger.info(' Barrier Reply received')
        msg = ev.msg
        datapath = msg.datapath
        ofp = datapath.ofproto
        # Fix me: remove dummy flow
        load_balancer.flag_update(self.ctlr_id, flag='MigrationEnd', status=True)
        # Fix me: Indicates the end of Migration, currently commenting it out for debugging purposes
        self.mig_end_status = True

        #To fetch datapath
        self.mip_flag_status = load_balancer.flag_check(self.ctlr_id, flag='MigrationInProgress')
        datapath_role = datapath
        datapath_role.id = int(self.mip_flag_status['dpid'])

        self.send_role_request(datapath_role, ofp.OFPCR_ROLE_SLAVE, stats_clear=True)


    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        # If you hit this you might want to increase
        # the "miss_send_length" of your switch

        if ev.msg.msg_len < ev.msg.total_len:
            self.logger.debug("packet truncated: only %s of %s bytes",
                              ev.msg.msg_len, ev.msg.total_len)
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']
        dpid = datapath.id
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        # migration start
        pkt_icmp = pkt.get_protocol(icmp.icmp)
        if pkt_icmp:
            load_balancer.stats_update(self.ctlr_id, dpid)

        # across both the controllers. Specify other controller's id
        cmf_status = self.check_cmf(1)
        #print("\ncmf status is {}\n".format(cmf_status))
        #print("Active mig status: {}".format(self.ActiveMigrationProcess))

        if pkt_icmp:
            # Unloaded Controller Logic Block
            if (not self.ActiveMigrationProcess) and (cmf_status != '2'):
                if not self.status_mip_updated:
                    self.mip_status = load_balancer.flag_check(self.ctlr_id, flag='MigrationInProgress')
                    if self.mip_status['status'] == 'True':
                        print("\n\n\n$$$$$ Start of Migration for Switch {} at Controller {} as Unloaded $$$$$\n\n\n".format(self.mip_status['dpid'], self.ctlr_id))

                        self.ActiveMigrationProcess = True
                        load_balancer.update_cmf_status(self.ctlr_id, 1)

                        #self.start_time = time.time()
                        #datapath_role_pkl = self.mip_status['datapath']
                        #datapath_role = pickle.loads(datapath_role_pkl)
                        self.status_mip_updated = True
                        datapath_role = datapath
                        datapath_role.id = int(self.mip_status['dpid'])
                        #print("**************** Datapath role fetched from db is {} ****************".format(datapath_role))
                        self.send_role_request(datapath_role, ofproto.OFPCR_ROLE_EQUAL)

            if self.flag_mis_updated:
                mie_status = load_balancer.flag_check(self.ctlr_id, flag='MigrationEnd')
                if mie_status == 'True':
                    #datapath_role = mip_status['datapath']
                    datapath_role = datapath
                    datapath_role.id = int(self.mip_status['dpid'])
                    self.send_role_request(datapath_role, ofproto.OFPCR_ROLE_MASTER, stats_clear=True)
                    self.flag_mis_updated = False
                    #self.ActiveMigrationProcess = False

            # Loaded Controller Logic Block
            if (not self.ActiveMigrationProcess) and (cmf_status == '0'):
                #time.sleep(.1)
                mig_status = False
                mip_check = load_balancer.flag_check(self.ctlr_id, flag='MigrationInProgress')
                if (not self.flag_mip_updated) and (self.mig_end_status == True) and (mip_check['status']=='False'):
                    mig_status, info = load_balancer.check_migration(self.ctlr_id)
                    print("Result of check_migration status:{} info:{}".format(mig_status, info))
                    if mig_status == True and not self.flag_mip_updated:
                        print("\n\n\n$$$$$ Start of Migration for Switch {} at Controller {} as Loaded $$$$$\n\n\n".format(dpid, self.ctlr_id))
                        self.ActiveMigrationProcess = True
                        load_balancer.update_cmf_status(self.ctlr_id, 1)
                        load_balancer.flag_update(self.ctlr_id, flag='MigrationInProgress', status=True, datapath=datapath,
                                                  dpid=dpid)
                        load_balancer.flag_update(self.ctlr_id, flag='MigrationEnd', status=False)
                        # print("updated data path {}".format(datapath))
                        self.flag_mip_updated = True
                        self.mig_end_status = False

            if self.flag_mip_updated:
                mig_start = load_balancer.flag_check(self.ctlr_id, flag='MigrationStart')
                if mig_start == 'True':
                    # Fix me:add dummy flow here..
                    load_balancer.update_cmf_status(self.ctlr_id, 2)
                    self.mip_flag_status = load_balancer.flag_check(self.ctlr_id, flag='MigrationInProgress')
                    datapath_barrier = datapath
                    datapath_barrier.id = int(self.mip_flag_status['dpid'])
                    self.send_barrier_request(datapath_barrier)
                    self.flag_mip_updated = False


        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # ignore lldp packet
            return
        dst = eth.dst
        src = eth.src

        self.mac_to_port.setdefault(dpid, {})
        '''
        pkt_icmp = pkt.get_protocol(icmp.icmp)
        if pkt_icmp:
            self.logger.info("packet in %s %s %s %s", dpid, src, dst, in_port)
        '''

        # learn a mac address to avoid FLOOD next time.
        self.mac_to_port[dpid][src] = in_port

        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]

        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data
        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)

    @set_ev_cls(ofp_event.EventOFPErrorMsg,
                [HANDSHAKE_DISPATCHER, CONFIG_DISPATCHER, MAIN_DISPATCHER])
    def on_error_msg(self, ev):
        msg = ev.msg
        # print('receive a error message: %s' % (msg))

    @set_ev_cls(ofp_event.EventOFPRoleReply, MAIN_DISPATCHER)
    def on_role_reply(self, ev):
        msg = ev.msg
        dp = msg.datapath
        dpid = dp.id
        ofp = dp.ofproto
        role = msg.role
        # self.send_role_request(dp, ofp.OFPCR_ROLE_MASTER, self.gen_id)
        print('Received Role reply on Master for Role: {} from switch: {}'.format(self.role_string_list[msg.role],dp.id))
        if self.ActiveMigrationProcess:
            if role == 1:
                print('\n\n$$$$$ Role of Controller {} changed to equal for dpid: {} $$$$$\n\n'.format(self.ctlr_id, dp.id))
                load_balancer.flag_update(self.ctlr_id, flag='MigrationStart', status=True)
                self.flag_mis_updated = True
            if role == 2:
                print('\n\n$$$$$$ Role of Controller: {} changed to Master for dpid: {} $$$$$$\n\n'.format(self.ctlr_id, dp.id))
                #print("\n\n***** Migration time is {} *****\n\n".format(self.stop_time - self.start_time))
                # Reset flags
                load_balancer.flag_update(self.ctlr_id, flag='MigrationInProgress', status=False, datapath=dp,
                                          dpid=dpid)
                load_balancer.flag_update(self.ctlr_id, flag='MigrationStart', status=False)
                self.ActiveMigrationProcess = False
                load_balancer.update_cmf_status(self.ctlr_id, 0)
                self.status_mip_updated = False

            if role == 3:
                print('\n\n$$$$$ Role of Controller: {} changed to Slave for dpid: {} $$$$$\n\n'.format(self.ctlr_id, dp.id))
                self.ActiveMigrationProcess = False
                load_balancer.update_cmf_status(self.ctlr_id, 0)

    def send_role_request(self, datapath, role, stats_clear=False):
        print("Role request from Slave controller for dpid: {} and role: {}".format(datapath.id, self.role_string_list[role]))
        ofp_parser = datapath.ofproto_parser
        dpid = datapath.id
        if stats_clear:
            # Reset the stat counter to zero
            load_balancer.stats_clear(self.ctlr_id, dpid)
        generation_id = load_balancer.get_gen_id()
        msg = ofp_parser.OFPRoleRequest(datapath, role, generation_id)
        datapath.send_msg(msg)

    def check_cmf(self, ctlr_id):
        cmf_dict = load_balancer.get_cmf_status()
        for key, val in cmf_dict.items():
            if key == str(ctlr_id):
                #print("Value returned in check cmf: {}".format(val))
                return val
