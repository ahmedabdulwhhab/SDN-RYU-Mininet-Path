# -*- coding: utf-8 -*-
#sudo apt install python3-pymongo
#or 
#Use
#sudo git clone https://github.com/mongodb/mongo-python-driver.git pymongo
#cd pymongo/
#python3 setup.py install


import os, sys
import pymongo
from pymongo import MongoClient

'''
Controller = {
ID:
Role: { dpid: role, dpid:role, dpid:role…}
Stats: {dpid:PacIN_count, dpid:PacIN_count, dpid:PacIN_count…}
}

flags = {"MigrationInProgress":
                  {"status": "False",
                    "dpid": "0",
                    "datapath": "0"}
                "MigrationStart":"False",
                "MigrationEnd": "True"}

gen_id = {"value":"1"}

Central Migration Flag
cmf = {"1":"0", "2":"0"}
0 - No Migration in progress
1 - Migration just started, action required
2 - Migration in the middle, no new migrations.

'''
MAX_PACIN_COUNT = 150
#ctlr_id = 0
id_map = {} #To maintain ctlr id and object id mapping

client = MongoClient('localhost', 27017)
#client = MongoClient('mongodb://18.219.185.25:27017/')
db = client.elastiCon #db name: elastiCon
controllers = db.controllers #Document name: controllers - To keep track of controller data
flags = db.flags #Document name: flags - To track various flags during migration
gen_id = db.gen_id
cmf = db.cmf


def add_new_controller(ctlr_id):
    """
    To be called when a New controller comes up.
    The function creates an entry for each controller and gives it a unique ID.
    :return: Return the unique ID which the controller has to use in all further transactions.
    """
    #global ctlr_id
    #ctlr_id += 1
    id = ctlr_id
    ctlr_info = {"id":str(id),
                 "role":"",
                 "stats":""}
    ins_id = controllers.insert_one(ctlr_info).inserted_id
    print("Controller info inserted with ID: {}".format(ctlr_id))
    id_map[ctlr_id] = ins_id
    return ctlr_id

def stats_update(ctlr_id, dpid, pack_type="PACKIN"):
    """
    Update the PacketIN count per switch
    :param ctlr_id: Requesting controller's ID. To uniquely identify an entry in the database
    :param dpid: To identify the switch for which PacketIN count should be updated
    :param pack_type: Which stats to be updated. Currently dealing with PacketIN only
    :return: True if the update is successful
    """
    entry = controllers.find_one({"id": str(ctlr_id)})
    #Read and update PacketIN count
    #print("entry get stats is: {}".format(entry.get('stats')))
    if entry.get('stats') != "":
        try:
            pack_in_cnt = int(entry.get('stats')[str(dpid)])
        except KeyError:
            # An entry is present, but not of this dpid.
            entry['stats'][str(dpid)] = '0'
            controllers.update_one({'id': str(ctlr_id)}, {"$set": entry}, upsert=False)
            pack_in_cnt = 0

    else:
        #If an entry isn't populated, create it. Only used for first time
        #entry['stats'][str(dpid)] = '0'
        controllers.update_one({'id': str(ctlr_id)},{"$set": {'stats':{str(dpid):'0'}}}, upsert=False)
        pack_in_cnt = 0

    pack_in_cnt += 1
    #All database entries to be updated in str format
    entry['stats'][str(dpid)] = str(pack_in_cnt)
    controllers.update_one({"id":str(ctlr_id)}, {"$set": entry}, upsert=False)
    print("PacketIN count updated on Controller {} for Switch {} Count: {}".format(ctlr_id, dpid, pack_in_cnt))
    return True

def stats_clear(ctlr_id, dpid):
    """
    Clear switch stats once migration is done
    :param ctlr_id: Requesting controller's ID. To uniquely identify an entry in the database
    :param dpid: To identify the switch for which PacketIN count should be updated
    :return: True if the update is successful
    """
    entry = controllers.find_one({"id": str(ctlr_id)})
    pack_in_count = int(entry.get('stats')[str(dpid)])
    print("Clearing PacketIN count of {} on switch: {}".format(pack_in_count, dpid))
    entry['stats'][str(dpid)] = '0'
    controllers.update_one({"id": str(ctlr_id)}, {"$set": entry}, upsert=False)
    return True


def check_migration(ctlr_id):
    """
    To check for the PacketIN counts to know if the migration is needed
    :param ctlr_id: Requesting controller's ID
    :return: Decision, Switch on which decision is to be taken
    """
    #print("\nChecking if Migration is required... ")
    entry = controllers.find_one({"id": str(ctlr_id)})
    #Read the PacketIN count and take a decision
    stats_dict = entry.get('stats')
    for dpid in stats_dict:
        if int(stats_dict[str(dpid)]) > MAX_PACIN_COUNT:
            print("Migration Required!!\n")
            return True, dpid
    #print("Migration Not required..\n")
    return False, 0


def flag_update(ctlr_id, flag='MigrationInProgress', status=False, datapath='', dpid=''):
    """
    This function updates the flags in the db as requested by the controller
    :param ctlr_id: Requesting controller's ID
    :param flag: Flag to be updated (Currently dealing with Migration Progress flag only)
    :param status: Status of the flag (Ideally it has to be a dictionary, keeping it like this for simplicity)
    :return: None
    """
    # First check if the 'Flag' document is created. If not, create it and then proceed
    # Only first controller would find the Document empty and create it with default values
    #print("\nFlag update called for {} with status {}".format(flag, status))
    entry = flags.find_one()
    if not entry:
        print("Error Updating flag\n")
    else:
        if flag=='MigrationInProgress':
            # Fix me: Test pending
            Mig_flg = entry['MigrationInProgress']
            Mig_flg['status'] = str(status)
            Mig_flg['dpid'] = str(dpid)
            Mig_flg['datapath'] = str(datapath)
            flags.update_one({'MigrationEnd': 'True'}, {"$set": {'MigrationInProgress': Mig_flg}})
        elif flag=='MigrationStart' or flag=='MigrationEnd':
            entry[flag] = str(status)
            flags.update_one({'MigrationInProgress.status': 'True'}, {"$set": {flag: str(status)}})
        else:
            print("Flag error\n")


def flag_check(ctlr_id, flag='MigrationInProgress'):
    """
    This function is called by the controller to check the status of any flag
    :param ctlr_id: Requesting controller's ID
    :param flag: Flag whose status has to be checked
    :return: Status of the flag
    """
    #print("\nFlag check called for {}".format(flag))
    entry = flags.find_one()
    if not entry:
        print("Error in reading Flags from Database, creating entry\n")
        if not entry:
            fl = {"MigrationInProgress":
                      {"status": "False",
                       "dpid": "0",
                       "datapath": "0"},
                  "MigrationStart": "False",
                  "MigrationEnd": "True"}
            flags.insert_one(fl)
        return
    else:
        status = entry[flag]
        #print("Status returned: {}".format(status))
        return status

def get_gen_id():
    """
    Generates a gen_id to be used for Role Request
    """
    entry = gen_id.find_one()
    if not entry:
        # gen_id document doesn't exist, Creating one...
        id = {'value': '1'}
        gen_id.insert_one(id)
        value = 1
    else:
        value = entry['value']
    print("get gen_id returns {}".format(value))
    val_new = int(value) + 1
    gen_id.update_one({'value': str(value)}, {'$set': {'value': str(val_new)}})
    print("gen id val updated to {}".format(val_new))
    return int(value)

def get_cmf_status():
    """
    Get status of the Central Migration Flag
    """
    entry = cmf.find_one()
    if not entry:
        # cmf document doesn't exist, Creating one...
        cmf_entry = {'1':'0', '2':'0'}
        cmf.insert_one(cmf_entry)
    #print("In get cmf status, returning {}".format(cmf.find_one()))
    return(cmf.find_one())

def update_cmf_status(ctlr_id, status):
    """
    Update status of Central Migration Flag
    """
    entry = cmf.find_one()
    id = entry['_id']
    cmf.update_one({'_id': id}, {'$set':{str(ctlr_id): str(status)}})
