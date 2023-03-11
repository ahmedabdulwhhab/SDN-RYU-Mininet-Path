# REST API
#

# Retrieve the switch stats
#
# get the list of all switches
# GET /stats/switches           curl http://localhost:8080/stats/switches
#
# get the desc stats of the switch
# GET /stats/desc/<dpid>        curl http://localhost:8080/stats/desc/1
#
# get flows desc stats of the switch
# GET /stats/flowdesc/<dpid>    curl http://localhost:8080/stats/flowdesc/1
#
# get flows desc stats of the switch filtered by the fields
# POST /stats/flowdesc/<dpid>
#
# get flows stats of the switch
# GET /stats/flow/<dpid>        curl http://localhost:8080/stats/flow/1       
#
# get flows stats of the switch filtered by the fields
# POST /stats/flow/<dpid>
#
# get aggregate flows stats of the switch
# GET /stats/aggregateflow/<dpid>
#
# get aggregate flows stats of the switch filtered by the fields
# POST /stats/aggregateflow/<dpid>
#
# get table stats of the switch
# GET /stats/table/<dpid>
#
# get table features stats of the switch
# GET /stats/tablefeatures/<dpid>
#
# get ports stats of the switch
# GET /stats/port/<dpid>[/<port>]
# Note: Specification of port number is optional
#
# get queues stats of the switch
# GET /stats/queue/<dpid>[/<port>[/<queue_id>]]
# Note: Specification of port number and queue id are optional
#       If you want to omitting the port number and setting the queue id,
#       please specify the keyword "ALL" to the port number
#       e.g. GET /stats/queue/1/ALL/1
#
# get queues config stats of the switch
# GET /stats/queueconfig/<dpid>[/<port>]
# Note: Specification of port number is optional
#
# get queues desc stats of the switch
# GET /stats/queuedesc/<dpid>[/<port>[/<queue_id>]]
# Note: Specification of port number and queue id are optional
#       If you want to omitting the port number and setting the queue id,
#       please specify the keyword "ALL" to the port number
#       e.g. GET /stats/queuedesc/1/ALL/1
#
# get meter features stats of the switch
# GET /stats/meterfeatures/<dpid>
#
# get meter config stats of the switch
# GET /stats/meterconfig/<dpid>[/<meter_id>]
# Note: Specification of meter id is optional
#
# get meter desc stats of the switch
# GET /stats/meterdesc/<dpid>[/<meter_id>]
# Note: Specification of meter id is optional
#
# get meters stats of the switch
# GET /stats/meter/<dpid>[/<meter_id>]
# Note: Specification of meter id is optional
#
# get group features stats of the switch
# GET /stats/groupfeatures/<dpid>
#
# get groups desc stats of the switch
# GET /stats/groupdesc/<dpid>[/<group_id>]
# Note: Specification of group id is optional (OpenFlow 1.5 or later)
#
# get groups stats of the switch
# GET /stats/group/<dpid>[/<group_id>]
# Note: Specification of group id is optional
#
# get ports description of the switch
# GET /stats/portdesc/<dpid>[/<port_no>]
# Note: Specification of port number is optional (OpenFlow 1.5 or later)

# Update the switch stats
#
# add a flow entry
# POST /stats/flowentry/add     
#tested ok
#curl -X POST -d '{"dpid": 1,"cookie": 1,"cookie_mask": 1,"table_id": 0,"idle_timeout": 3000,"hard_timeout": 3000,"priority": 1,"flags": 1,"match":{"in_port": 1,"dl_dst": "00:00:00:00:00:02","dl_src": "00:00:00:00:00:01"},"actions":[{"type":"OUTPUT","port": 2}]}' http://localhost:8080/stats/flowentry/add
#curl -X POST -d '{"dpid": 1,"cookie": 1,"cookie_mask": 1,"table_id": 0,"priority": 10,"flags": 1,"match":{"eth_type" : 2048,"ipv4_src" : "172.16.20.0/255.255.255.0" },"actions":[{"type":"OUTPUT","port": 2}]}' http://localhost:8080/stats/flowentry/add  
#curl -X POST -d '{"dpid": 1,"cookie": 1,"cookie_mask": 1,"table_id": 0,"priority": 10,"flags": 1,"match":{"eth_type" : 2048,"ipv4_src" : "172.16.20.0/255.255.255.0" ,"ipv4_dst" : "172.16.20.0/255.255.255.0"},"actions":[{"type":"OUTPUT","port": 2}]}' http://localhost:8080/stats/flowentry/add  
#curl -X POST -d '{"dpid": 1,"cookie": 1,"cookie_mask": 1,"table_id": 0,"idle_timeout": 3000,"hard_timeout": 3000,"priority": 10,"flags": 1,"match":{"eth_type":2054,"in_port": 1,"dl_dst": "00:00:00:00:00:02","dl_src": "00:00:00:00:00:01"},"actions":[{"type":"DROP"}]}' http://localhost:8080/stats/flowentry/add
#curl -X POST -d '{"dpid": 1,"cookie": 1,"cookie_mask": 1,"table_id": 0 ,"priority": 10,"flags": 1,"match":{"eth_type":2054,"arp_spa": "10.0.0.11","arp_tpa": "10.0.0.100"},"actions":[{"type":"DROP"}]}' http://localhost:8080/stats/flowentry/add
#curl -X POST -d '{"dpid": 1,"cookie": 1,"cookie_mask": 1,"table_id": 0,"priority": 10,"flags": 1,"match":{"eth_type" : 2048,"ipv4_src":"10.0.0.2","ipv4_dst" : "10.0.0.1","ip_proto" : 17,"tp_src": 5694, "udp_dst": 5001},"actions":[{"type":"DROP"}]}' http://localhost:8080/stats/flowentry/add
"""              TESTED
curl -X POST -d '{
    "dpid": 1,
    "cookie": 1,
    "cookie_mask": 1,
    "table_id": 0,
    "priority": 100,
    "flags": 1,
    "match":{
        "eth_type" : 2048,
        "ipv4_dst":"172.16.20.1",
        "ipv4_src" : "172.16.20.10",
        "ip_proto" : 6,
        "tcp_dst": 54321
        }
    ,"actions":[
        {"type": "DEC_NW_TTL"},
        {"type":"OUTPUT","port": 2},
        {"type":"SET_FIELD","field":"ipv4_dst","value":"172.16.10.10"},
        {"type":"SET_FIELD","field":"ipv4_src","value":"172.16.20.10"},
        {"type":"SET_FIELD","field":"tcp_dst","value":12345}        
        ]}' http://localhost:8080/stats/flowentry/add
        
        
        
        
    "dpid": 1,
    "cookie": 1,
    "cookie_mask": 1,
    "table_id": 0,
    "priority": 100,
    "flags": 1,
    "match":{
        "eth_type" : 2048,
        "ipv4_dst":"172.16.20.1",
        "ipv4_src" : "172.16.20.10",
        "ip_proto" : 6,
        "tcp_dst": 54321
        }
    ,"actions":[
        {"type": "DROP"}
        ]}' http://localhost:8084/stats/flowentry/add        
"""
"""
curl -X POST -d '{
    "dpid": 1,
    "cookie": 1,
    "cookie_mask": 1,
    "table_id": 0,
    "priority": 10,
    "flags": 1,
    "match":{
        "eth_type" : 2048,
        "ipv4_src":"10.0.0.2",
        "ipv4_dst" : "10.0.0.1",
        "ip_proto" : 17,
        "tp_src": 56944,
        "udp_dst": 5001}
    ,"actions":[
        {"type":"SET_FIELD","field":"ipv4_dst","value":"10.0.0.1"},
        {"type":"SET_FIELD","field":"ipv4_src","value":"10.0.0.2"},
        {"type":"SET_FIELD","field":"udp_src","value":40364},
        {"type":"SET_FIELD","field":"udp_dst","value":5001}        
        ]}' http://localhost:8080/stats/flowentry/add
 """
 """
 curl -X POST -d '{
    "dpid": 1,
    "cookie": 1,
    "cookie_mask": 1,
    "table_id": 0,
    "priority": 100,
    "flags": 1,
    "match":{
        "eth_type" : 2048,
        "ipv4_dst":"172.16.20.100",
        "ipv4_src" : "172.16.20.10",
        "ip_proto" : 17,
        "udp_dst": 54321
        }
    ,"actions":[
        {"type": "DEC_NW_TTL"},
        {"type":"OUTPUT","port": 2},
        {"type":"SET_FIELD","field":"eth_dst","value":"d6:82:cf:9f:ca:58"},
        {"type":"SET_FIELD","field":"eth_src","value":"ee:3a:e1:ca:78:53"},
        {"type":"SET_FIELD","field":"ipv4_dst","value":"172.16.10.10"},
        {"type":"SET_FIELD","field":"ipv4_src","value":"172.16.20.10"},
        {"type":"SET_FIELD","field":"udp_dst","value":12345}        
        ]}' http://localhost:8080/stats/flowentry/add
 """
#not tested
#eth_type = 2054 OUTPUT:CONTROLLER
#curl -X POST -d '{"dpid": 1,"cookie": 1,"cookie_mask": 1,"table_id": 0,"idle_timeout": 3000,"hard_timeout": 3000,"priority": 10,"flags": 1,"match":{"eth_type":2054,"in_port": 1,"dl_dst": "00:00:00:00:00:02","dl_src": "00:00:00:00:00:01"},"actions":[{"type":"DROP"}]}' http://localhost:8080/stats/flowentry/add
#eth_type = 2048
#curl -X POST -d '{"dpid": 1,"cookie": 1,"cookie_mask": 1,"table_id": 0,"priority": 10,"flags": 1,"match":{"eth_type" : 2048,"ipv4_src" : "172.16.20.0/255.255.255.0" },"actions":[{"type":"OUTPUT","port": 2}]}' http://localhost:8080/stats/flowentry/add
#curl -X POST -d '{"dpid": 1,"cookie": 1,"cookie_mask": 1,"table_id": 0,"priority": 10,"flags": 1,"match":{"ipv4_src":"172.16.20.0/24"},"actions":[{"type":"OUTPUT","port": 2}]}' http://localhost:8080/stats/flowentry/add
#curl -X POST -d '{"dpid": 1,"cookie": 1,"cookie_mask": 1,"table_id": 0,"priority": 10,"flags": 1,"match":{"eth_type" : 2048,"ipv4_src":"10.0.0.2","ipv4_dst" : "10.0.0.1","ip_proto" : 17,"tp_src": 56944, "udp_dst": 5001},"actions":[{"type":"SET_FIELD","field":"ipv4_dst","value":"10.0.0.1"}]}' http://localhost:8080/stats/flowentry/add

"""     ERROR Bad Match(4)
curl -X POST -d '{
    "dpid": 1,
    "cookie": 1,
    "cookie_mask": 1,
    "table_id": 0,
    "priority": 100,
    "flags": 1,
    "match":{
        "eth_type" : 2048,
        "ipv4_dst":"172.16.20.1",
        "ipv4_src" : "172.16.20.10",
        "ip_proto" : 6,
        "udp_dst": 54321
        }
    ,"actions":[
        {"type": "DEC_NW_TTL"},
        {"type":"OUTPUT","port": 2},
        {"type":"SET_FIELD","field":"eth_dst","value":"d6:82:cf:9f:ca:58"},
        {"type":"SET_FIELD","field":"eth_src","value":"ee:3a:e1:ca:78:53"},
        {"type":"SET_FIELD","field":"ipv4_dst","value":"172.16.30.1"},
        {"type":"SET_FIELD","field":"ipv4_src","value":"172.16.20.10"},
        {"type":"SET_FIELD","field":"tcp_dst","value":12345}        
        ]}' http://localhost:8080/stats/flowentry/add
 """
"""     ERROR Bad Action(2)
curl -X POST -d '{
    "dpid": 1,
    "cookie": 1,
    "cookie_mask": 1,
    "table_id": 0,
    "priority": 100,
    "flags": 1,
    "match":{
        "eth_type" : 2048,
        "ipv4_dst":"172.16.20.1",
        "ipv4_src" : "172.16.20.10",
        "ip_proto" : 17,
        "udp_dst": 54321
        }
    ,"actions":[
        {"type": "DEC_NW_TTL"},
        {"type":"OUTPUT","port": 2},
        {"type":"SET_FIELD","field":"eth_dst","value":"d6:82:cf:9f:ca:58"},
        {"type":"SET_FIELD","field":"eth_src","value":"ee:3a:e1:ca:78:53"},
        {"type":"SET_FIELD","field":"ipv4_dst","value":"172.16.30.1"},
        {"type":"SET_FIELD","field":"ipv4_src","value":"172.16.20.10"},
        {"type":"SET_FIELD","field":"tcp_dst","value":12345}        
        ]}' http://localhost:8080/stats/flowentry/add
 """
 """     OK
curl -X POST -d '{
    "dpid": 1,
    "cookie": 1,
    "cookie_mask": 1,
    "table_id": 0,
    "priority": 100,
    "flags": 1,
    "match":{
        "eth_type" : 2048,
        "ipv4_dst":"172.16.20.1",
        "ipv4_src" : "172.16.20.10",
        "ip_proto" : 6,
        "tcp_dst": 54321
        }
    ,"actions":[
        {"type": "DEC_NW_TTL"},
        {"type":"OUTPUT","port": 2},
        {"type":"SET_FIELD","field":"eth_dst","value":"d6:82:cf:9f:ca:58"},
        {"type":"SET_FIELD","field":"eth_src","value":"ee:3a:e1:ca:78:53"},
        {"type":"SET_FIELD","field":"ipv4_dst","value":"172.16.30.1"},
        {"type":"SET_FIELD","field":"ipv4_src","value":"172.16.20.10"},
        {"type":"SET_FIELD","field":"tcp_dst","value":12345}        
        ]}' http://localhost:8080/stats/flowentry/add
 """
 
 

  """     under test


curl -X POST -d '{
    "dpid": 2,
    "cookie": 1,
    "cookie_mask": 1,
    "table_id": 0,
    "priority": 2000,
    "flags": 1,
    "match":{
        "eth_type" : 2048,
        #eth_dst= "bb:aa:bb:dd:22:dd",
        "ipv4_dst":"172.16.10.100"

        #,
        #"ip_proto" : 6,
        #"tcp_dst": 54321
        }
    ,"actions":[
        {"type": "DEC_NW_TTL"},
        {"type":"OUTPUT","port": 1},
        {"type":"SET_FIELD","field":"eth_dst","value":"00:00:01:00:00:00"},
        {"type":"SET_FIELD","field":"ipv4_dst","value":"172.16.10.10"},
        {"type":"SET_FIELD","field":"ipv4_src","value":"172.16.20.100"},  # to leave network
        #{"type":"SET_FIELD","field":"tcp_dst","value":12345}        
        ]}' http://localhost:8080/stats/flowentry/add  

curl -X POST -d '{
    "dpid": 1,
    "cookie": 1,
    "cookie_mask": 1,
    "table_id": 0,
    "priority": 2000,
    "flags": 1,
    "match":{
        "eth_type" : 2048,
        #"eth_dst": "bb:aa:bb:dd:22:dd",
        "ipv4_dst":"172.16.20.100"
        #,
        #"ip_proto" : 6,
        #"tcp_dst": 54321
        }
    ,"actions":[
        {"type": "DEC_NW_TTL"},
        {"type":"OUTPUT","port": 1},
        {"type":"SET_FIELD","field":"eth_dst","value":"00:00:02:00:00:00"},
        {"type":"SET_FIELD","field":"ipv4_dst","value":"172.16.20.10"},
        {"type":"SET_FIELD","field":"ipv4_src","value":"172.16.10.100"},
        #{"type":"SET_FIELD","field":"tcp_dst","value":12345}        
        ]}' http://localhost:8080/stats/flowentry/add         
        
        
	DEC_NW_TTL
	DEC_NW_TTL
SET_FIELD: eth_src:ce:af:56:c6:2c:19
SET_FIELD: eth_dst:00:00:02:00:00:00
OUTPUT:1

        
curl -X POST -d '{
    "dpid": 2,
    "cookie": 1,
    "cookie_mask": 1,
    "table_id": 0,
    "priority": 2000,
    "flags": 1,
    "match":{
        "eth_type" : 2048,
        "ipv4_dst" : "172.16.10.100"
        #,"ipv4_src" : "172.16.10.100"
        #,
        #"ip_proto" : 6,
        #"tcp_dst": 54321
        }
    ,"actions":[
        {"type": "DEC_NW_TTL"},
        {"type":"OUTPUT","port": 1},
        {"type":"SET_FIELD","field":"eth_dst","value":"00:00:02:00:00:00"},
        {"type":"SET_FIELD","field":"eth_src","value":"d2:e1:95:8d:eb:0a"},
        {"type":"SET_FIELD","field":"ipv4_dst","value":"172.16.10.10"},
        #{"type":"SET_FIELD","field":"ipv4_src","value":"172.16.10.100"},
        #{"type":"SET_FIELD","field":"tcp_dst","value":12345}        
        ]}' http://localhost:8080/stats/flowentry/add
 """




""" 25/2
curl -X POST -d '{
    "dpid": 51,
    "cookie": 1,
    "cookie_mask": 1,
    "table_id": 0,
    "priority": 2000,
    "flags": 1,
    "match":{
        "dl_type" : 2048,
        "ipv4_dst" : "172.16.10.120"
        }
    ,"actions":[
        {"type": "SET_NW_DST", "nw_dst": "172.16.10.12"},
        {"type":"OUTPUT","port": 2},        
        ]}' http://localhost:8080/stats/flowentry/add 
"""

25/2
curl -X POST -d '{
    "dpid": 51,
    "cookie": 0,
    "table_id": 0,
    "priority": 2000,
    "flags": 1,
    "match":{
        "eth_type" : 2048,
        "ipv4_dst" : "172.16.10.120"
        }
    ,"actions":[
        #{"type": "DEC_NW_TTL"},
        {"type":"OUTPUT","port": 2},   
        #{"type":"SET_FIELD","field":"eth_dst","value":"02:81:aa:0e:8d:5b"},
        #{"type":"SET_FIELD","field":"eth_src","value":"fa:86:26:1d:4b:4d"},        
        {"type":"SET_FIELD","field":"ipv4_dst","value":"172.16.10.12"},
        ]}' http://localhost:8080/stats/flowentry/add 

curl -X POST -d '{
    "dpid": 51,
    "cookie": 1,
    "cookie_mask": 1,
    "table_id": 0,
    "priority": 2000,
    "flags": 1,
    "match":{
        "eth_type" : 2048,
        "ipv4_dst" : "172.16.10.120"
        #,"ipv4_src" : "172.16.10.100"
        #,
        #"ip_proto" : 6,
        #"tcp_dst": 54321
        }
    ,"actions":[
        {"type": "DEC_NW_TTL            #SET_NW_TTL bad
        {"type":"OUTPUT","port": 2},
        {"type":"SET_FIELD","field":"ipv4_dst","value":"172.16.10.12"}
        #{"type":"SET_FIELD","field":"tcp_dst","value":12345}        
        ]}' http://localhost:8080/stats/flowentry/add
 
 """
curl -X POST -d '{
    "dpid": 51,
    "cookie": 0,
    "table_id": 0,
    "priority": 2000,
    "flags": 1,
    "match":{
        "eth_type" : 2048,
        "arp_tpa" : "172.16.10.120"
        }
    ,"actions":[
        #{"type": "DEC_NW_TTL"},
        {"type":"OUTPUT","port": 2},   
        #{"type":"SET_FIELD","field":"eth_dst","value":"02:81:aa:0e:8d:5b"},
        #{"type":"SET_FIELD","field":"eth_src","value":"fa:86:26:1d:4b:4d"},        
        {"type":"SET_FIELD","field":"ipv4_dst","value":"172.16.10.12"},
        ]}' http://localhost:8080/stats/flowentry/add 


curl -X POST -d '{
    "dpid": 51,
    "cookie": 0,
    "table_id": 0,
    "priority": 2000,
    "flags": 1,
    "match":{
        "eth_type" : 2054,
        "arp_tpa" : "172.16.10.120"
        }
    ,"actions":[
        #{"type": "DEC_NW_TTL"},
        {"type":"OUTPUT","port": 2},   
        #{"type":"SET_FIELD","field":"eth_dst","value":"02:81:aa:0e:8d:5b"},
        #{"type":"SET_FIELD","field":"eth_src","value":"fa:86:26:1d:4b:4d"},        
        {"type":"SET_FIELD","field":"arp_tpa","value":"172.16.10.12"},
        ]}' http://localhost:8080/stats/flowentry/add 
"""
"""

curl -X POST -d '{
    "dpid": 2,
    "cookie": 1,
    "cookie_mask": 1,
    "table_id": 0,
    "priority": 2000,
    "flags": 1,
    "match":{
        "eth_type" : 2048,
        "icmpv4_type": 5,
         "ip_proto": 1,     #ICMP
        "ipv4_dst" : "172.16.10.100"
        #,
        #"ip_proto" : 6,
        #"tcp_dst": 54321
        }
    ,"actions":[
        {"type": "DEC_NW_TTL"},
        {"type":"OUTPUT","port": 1},
        {"type":"SET_FIELD","field":"eth_dst","value":"00:00:02:00:00:00"},
        {"type":"SET_FIELD","field":"eth_src","value":"d2:e1:95:8d:eb:0a"},
        {"type":"SET_FIELD","field":"ipv4_dst","value":"172.16.10.10"},
        #{"type":"SET_FIELD","field":"ipv4_src","value":"172.16.10.100"},
        #{"type":"SET_FIELD","field":"tcp_dst","value":12345}        
        ]}' http://localhost:8080/stats/flowentry/add
        



curl -X POST -d '{
    "dpid": 51,
    "cookie": 1,
    "cookie_mask": 1,
    "table_id": 0,
    "priority": 2000,
    "flags": 1,
    "match":{
        "eth_type" : 2048,
        "icmpv4_type": 5,
         "ip_proto": 1,     #ICMP
        "ipv4_dst" : "172.16.10.120"
        #,
        #"ip_proto" : 6,
        #"tcp_dst": 54321
        }
    ,"actions":[
        {"type": "DEC_NW_TTL"},
        {"type":"OUTPUT","port": 2},
        {"type":"SET_FIELD","field":"eth_dst","value":"00:00:02:00:00:00"},
        {"type":"SET_FIELD","field":"eth_src","value":"d2:e1:95:8d:eb:0a"},
        {"type":"SET_FIELD","field":"ipv4_dst","value":"172.16.10.10"},
        #{"type":"SET_FIELD","field":"ipv4_src","value":"172.16.10.12"},
        #{"type":"SET_FIELD","field":"tcp_dst","value":12345}        
        ]}' http://localhost:8080/stats/flowentry/add



curl -X POST -d '{
    "dpid": 51,
    "cookie": 1,
    "cookie_mask": 1,
    "table_id": 0,
    "priority": 2001,
    "flags": 1,
    "match":{
        "eth_type" : 2048,
        "icmpv4_type": 5,
         "ip_proto": 1,     #ICMP
        #"ipv4_dst" : "172.16.10.120"
        #,
        #"ip_proto" : 6,
        #"tcp_dst": 54321
        }
    ,"actions":[
        {"type": "DEC_NW_TTL"},
        {"type":"OUTPUT","port": 2},
        {"type":"SET_FIELD","field":"eth_dst","value":"00:00:02:00:00:00"},
        {"type":"SET_FIELD","field":"eth_src","value":"d2:e1:95:8d:eb:0a"},
        {"type":"SET_FIELD","field":"ipv4_dst","value":"172.16.10.12"},
        #{"type":"SET_FIELD","field":"ipv4_src","value":"172.16.10.12"},
        #{"type":"SET_FIELD","field":"tcp_dst","value":12345}        
        ]}' http://localhost:8080/stats/flowentry/add
        
curl -X POST -d '{
    "dpid": 51,
    "cookie": 0,
    "table_id": 0,
    "priority": 2000,
    "flags": 1,
    "match":{
        "dl_type" : 2048
        ,"eth_dst":"00:00:33:00:00:00"
        #,"ipv4_dst" : "172.16.10.120"
        }
    ,"actions":[
        {"type": "DEC_NW_TTL"},
        {"type":"OUTPUT","port": 2},   
        {"type":"SET_FIELD","field":"eth_dst","value":"00:00:33:00:00:33"},
        #{"type":"SET_FIELD","field":"eth_src","value":"fa:86:26:1d:4b:4d"},        
        {"type":"SET_FIELD","field":"ipv4_dst","value":"172.16.10.12"},
        ]}' http://localhost:8080/stats/flowentry/add         
        
        
curl -X POST -d '{"dpid": 1,"cookie": 1,"cookie_mask": 1,"table_id": 0,"priority": 10,"flags": 1,"match":{"ipv4_src":"172.16.20.0/24"},"actions":[{"type":"OUTPUT","port": 2}]}' http://localhost:8080/stats/flowentry/add
curl -X POST -d '{"dpid": 1,"cookie": 1,"cookie_mask": 1,"table_id": 0,"priority": 10,"flags": 1,"match":{"ipv4_src":"172.16.20.0/24"},"actions":[{"type":"OUTPUT","port": 2}]}' http://localhost:8080/stats/flowentry/add
curl -X POST -d '{"dpid": 1,"cookie": 1,"cookie_mask": 1,"table_id": 0,"priority": 10,"flags": 1,"match":{"ipv4_src":"172.16.20.0/24"},"actions":[{"type":"OUTPUT","port": 2}]}' http://localhost:8080/stats/flowentry/add
curl -X POST -d '{"dpid": 1,"cookie": 1,"cookie_mask": 1,"table_id": 0,"priority": 10,"flags": 1,"match":{"ipv4_src":"172.16.20.0/24"},"actions":[{"type":"OUTPUT","port": 2}]}' http://localhost:8080/stats/flowentry/add

curl -X POST -d '{"dpid": 1,"cookie": 1,"cookie_mask": 1,"table_id": 0,"priority": 10,"flags": 1,"match":{"ipv4_src":"172.16.20.0/24"},"actions":[{"type":"OUTPUT","port": 2}]}' http://localhost:8080/stats/flowentry/add


