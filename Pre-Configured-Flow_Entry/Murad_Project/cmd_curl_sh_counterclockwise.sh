echo switch 1
echo
curl -X POST -d '{
    "dpid": 1,
    "cookie": 1,
    "cookie_mask": 1,
    "table_id": 0,"idle_timeout": 240,
    "priority": 11,
    "flags": 1,
    "match":{
        "in_port" : 3,
        "eth_type" : 2048,
        "ipv4_src":  "10.0.0.2",
        "ipv4_dst" : "10.0.0.1",
        "ip_proto" : 1,
        }
    ,"actions":[
        {"type":"OUTPUT","port": 1},
        
        ]}' http://localhost:8080/stats/flowentry/add
		
echo
curl -X POST -d '{
    "dpid": 1,
    "cookie": 1,
    "cookie_mask": 1,
    "table_id": 0,"idle_timeout": 240,
    "priority": 11,
    "flags": 1,
    "match":{
        "in_port" : 3,
        "eth_type" : 2048,
        "ipv4_src":  "10.0.0.3",
        "ipv4_dst" : "10.0.0.1",
        "ip_proto" : 1,
        }
    ,"actions":[
        {"type":"OUTPUT","port": 1},
        
        ]}' http://localhost:8080/stats/flowentry/add		

echo
curl -X POST -d '{
    "dpid": 1,
    "cookie": 1,
    "cookie_mask": 1,
    "table_id": 0,"idle_timeout": 240,
    "priority": 11,
    "flags": 1,
    "match":{
        "in_port" : 3,
        "eth_type" : 2048,
        "ipv4_src":  "10.0.0.4",
        "ipv4_dst" : "10.0.0.1",
        "ip_proto" : 1,
        }
    ,"actions":[
        {"type":"OUTPUT","port": 1},
        
        ]}' http://localhost:8080/stats/flowentry/add		
		
echo
curl -X POST -d '{
    "dpid": 1,
    "cookie": 1,
    "cookie_mask": 1,
    "table_id": 0,"idle_timeout": 240,
    "priority": 11,
    "flags": 1,
    "match":{
        "in_port" : 1,
        "eth_type" : 2048,
        "ipv4_src":  "10.0.0.1",
        "ipv4_dst" : "10.0.0.3",
        "ip_proto" : 1,
        }
    ,"actions":[
        {"type":"OUTPUT","port": 2},
        
        ]}' http://localhost:8080/stats/flowentry/add		

echo
curl -X POST -d '{
    "dpid": 1,
    "cookie": 1,
    "cookie_mask": 1,
    "table_id": 0,"idle_timeout": 240,
    "priority": 11,
    "flags": 1,
    "match":{
        "in_port" : 1,
        "eth_type" : 2048,
        "ipv4_src":  "10.0.0.1",
        "ipv4_dst" : "10.0.0.2",
        "ip_proto" : 1,
        }
    ,"actions":[
        {"type":"OUTPUT","port": 2},
        
        ]}' http://localhost:8080/stats/flowentry/add		

echo
curl -X POST -d '{
    "dpid": 1,
    "cookie": 1,
    "cookie_mask": 1,
    "table_id": 0,"idle_timeout": 240,
    "priority": 11,
    "flags": 1,
    "match":{
        "in_port" : 1,
        "eth_type" : 2048,
        "ipv4_src":  "10.0.0.1",
        "ipv4_dst" : "10.0.0.4",
        "ip_proto" : 1,
        }
    ,"actions":[
        {"type":"OUTPUT","port": 2},
        
        ]}' http://localhost:8080/stats/flowentry/add		

echo
curl -X POST -d '{
    "dpid": 1,
    "cookie": 1,
    "cookie_mask": 1,
    "table_id": 0,"idle_timeout": 240,
    "priority": 11,
    "flags": 1,
    "match":{
        "in_port" : 3,
        "eth_type" : 2048,
        "ipv4_src":  "10.0.0.4",
        "ipv4_dst" : "10.0.0.2",
        "ip_proto" : 1,
        }
    ,"actions":[
        {"type":"OUTPUT","port": 2},
        
        ]}' http://localhost:8080/stats/flowentry/add		
		
echo
curl -X POST -d '{
    "dpid": 1,
    "cookie": 1,
    "cookie_mask": 1,
    "table_id": 0,"idle_timeout": 240,
    "priority": 11,
    "flags": 1,
    "match":{
        "in_port" : 3,
        "eth_type" : 2048,
        "ipv4_src":  "10.0.0.3",
        "ipv4_dst" : "10.0.0.2",
        "ip_proto" : 1,
        }
    ,"actions":[
        {"type":"OUTPUT","port": 2},
        
        ]}' http://localhost:8080/stats/flowentry/add		
		
echo
curl -X POST -d '{
    "dpid": 1,
    "cookie": 1,
    "cookie_mask": 1,
    "table_id": 0,"idle_timeout": 240,
    "priority": 11,
    "flags": 1,
    "match":{
        "in_port" : 3,
        "eth_type" : 2048,
        "ipv4_src":  "10.0.0.4",
        "ipv4_dst" : "10.0.0.3",
        "ip_proto" : 1,
        }
    ,"actions":[
        {"type":"OUTPUT","port": 2},
        
        ]}' http://localhost:8080/stats/flowentry/add		
		
		
echo --------------------------------------------------------

echo switch 2
echo
curl -X POST -d '{
    "dpid": 2,
    "cookie": 1,
    "cookie_mask": 1,
    "table_id": 0,"idle_timeout": 240,
    "priority": 11,
    "flags": 1,
    "match":{
        "in_port" : 2,
        "eth_type" : 2048,
        "ipv4_src":  "10.0.0.1",
        "ipv4_dst" : "10.0.0.2",
        "ip_proto" : 1,
        }
    ,"actions":[
        {"type":"OUTPUT","port": 1},
        
        ]}' http://localhost:8080/stats/flowentry/add
		
echo
curl -X POST -d '{
    "dpid": 2,
    "cookie": 1,
    "cookie_mask": 1,
    "table_id": 0,"idle_timeout": 240,
    "priority": 11,
    "flags": 1,
    "match":{
        "in_port" : 2,
        "eth_type" : 2048,
        "ipv4_src":  "10.0.0.3",
        "ipv4_dst" : "10.0.0.2",
        "ip_proto" : 1,
        }
    ,"actions":[
        {"type":"OUTPUT","port": 1},
        
        ]}' http://localhost:8080/stats/flowentry/add		

echo
curl -X POST -d '{
    "dpid": 2,
    "cookie": 1,
    "cookie_mask": 1,
    "table_id": 0,"idle_timeout": 240,
    "priority": 11,
    "flags": 1,
    "match":{
        "in_port" : 2,
        "eth_type" : 2048,
        "ipv4_src":  "10.0.0.4",
        "ipv4_dst" : "10.0.0.2",
        "ip_proto" : 1,
        }
    ,"actions":[
        {"type":"OUTPUT","port": 1},
        
        ]}' http://localhost:8080/stats/flowentry/add		
		
echo
curl -X POST -d '{
    "dpid": 2,
    "cookie": 1,
    "cookie_mask": 1,
    "table_id": 0,"idle_timeout": 240,
    "priority": 11,
    "flags": 1,
    "match":{
        "in_port" : 1,
        "eth_type" : 2048,
        "ipv4_src":  "10.0.0.2",
        "ipv4_dst" : "10.0.0.3",
        "ip_proto" : 1,
        }
    ,"actions":[
        {"type":"OUTPUT","port": 3},
        
        ]}' http://localhost:8080/stats/flowentry/add		

echo
curl -X POST -d '{
    "dpid": 2,
    "cookie": 1,
    "cookie_mask": 1,
    "table_id": 0,"idle_timeout": 240,
    "priority": 11,
    "flags": 1,
    "match":{
        "in_port" : 1,
        "eth_type" : 2048,
        "ipv4_src":  "10.0.0.2",
        "ipv4_dst" : "10.0.0.1",
        "ip_proto" : 1,
        }
    ,"actions":[
        {"type":"OUTPUT","port": 3},
        
        ]}' http://localhost:8080/stats/flowentry/add		

echo
curl -X POST -d '{
    "dpid": 2,
    "cookie": 1,
    "cookie_mask": 1,
    "table_id": 0,"idle_timeout": 240,
    "priority": 11,
    "flags": 1,
    "match":{
        "in_port" : 1,
        "eth_type" : 2048,
        "ipv4_src":  "10.0.0.2",
        "ipv4_dst" : "10.0.0.4",
        "ip_proto" : 1,
        }
    ,"actions":[
        {"type":"OUTPUT","port": 3},
        
        ]}' http://localhost:8080/stats/flowentry/add		

echo
curl -X POST -d '{
    "dpid": 2,
    "cookie": 1,
    "cookie_mask": 1,
    "table_id": 0,"idle_timeout": 240,
    "priority": 11,
    "flags": 1,
    "match":{
        "in_port" : 2,
        "eth_type" : 2048,
        "ipv4_src":  "10.0.0.1",
        "ipv4_dst" : "10.0.0.3",
        "ip_proto" : 1,
        }
    ,"actions":[
        {"type":"OUTPUT","port": 3},
        
        ]}' http://localhost:8080/stats/flowentry/add		
		
echo
curl -X POST -d '{
    "dpid": 2,
    "cookie": 1,
    "cookie_mask": 1,
    "table_id": 0,"idle_timeout": 240,
    "priority": 11,
    "flags": 1,
    "match":{
        "in_port" : 2,
        "eth_type" : 2048,
        "ipv4_src":  "10.0.0.1",
        "ipv4_dst" : "10.0.0.4",
        "ip_proto" : 1,
        }
    ,"actions":[
        {"type":"OUTPUT","port": 3},
        
        ]}' http://localhost:8080/stats/flowentry/add		
		
echo
curl -X POST -d '{
    "dpid": 2,
    "cookie": 1,
    "cookie_mask": 1,
    "table_id": 0,"idle_timeout": 240,
    "priority": 11,
    "flags": 1,
    "match":{
        "in_port" : 2,
        "eth_type" : 2048,
        "ipv4_src":  "10.0.0.4",
        "ipv4_dst" : "10.0.0.3",
        "ip_proto" : 1,
        }
    ,"actions":[
        {"type":"OUTPUT","port": 3},
        
        ]}' http://localhost:8080/stats/flowentry/add				
		
		
echo --------------------------------------------------------

echo switch 3
echo
curl -X POST -d '{
    "dpid": 3,
    "cookie": 1,
    "cookie_mask": 1,
    "table_id": 0,"idle_timeout": 240,
    "priority": 11,
    "flags": 1,
    "match":{
        "in_port" : 2,
        "eth_type" : 2048,
        "ipv4_src":  "10.0.0.1",
        "ipv4_dst" : "10.0.0.3",
        "ip_proto" : 1,
        }
    ,"actions":[
        {"type":"OUTPUT","port": 1},
        
        ]}' http://localhost:8080/stats/flowentry/add
		
echo
curl -X POST -d '{
    "dpid": 3,
    "cookie": 1,
    "cookie_mask": 1,
    "table_id": 0,"idle_timeout": 240,
    "priority": 11,
    "flags": 1,
    "match":{
        "in_port" : 2,
        "eth_type" : 2048,
        "ipv4_src":  "10.0.0.2",
        "ipv4_dst" : "10.0.0.3",
        "ip_proto" : 1,
        }
    ,"actions":[
        {"type":"OUTPUT","port": 1},
        
        ]}' http://localhost:8080/stats/flowentry/add		

echo
curl -X POST -d '{
    "dpid": 3,
    "cookie": 1,
    "cookie_mask": 1,
    "table_id": 0,"idle_timeout": 240,
    "priority": 11,
    "flags": 1,
    "match":{
        "in_port" : 2,
        "eth_type" : 2048,
        "ipv4_src":  "10.0.0.4",
        "ipv4_dst" : "10.0.0.3",
        "ip_proto" : 1,
        }
    ,"actions":[
        {"type":"OUTPUT","port": 1},
        
        ]}' http://localhost:8080/stats/flowentry/add		
		
echo
curl -X POST -d '{
    "dpid": 3,
    "cookie": 1,
    "cookie_mask": 1,
    "table_id": 0,"idle_timeout": 240,
    "priority": 11,
    "flags": 1,
    "match":{
        "in_port" : 1,
        "eth_type" : 2048,
        "ipv4_src":  "10.0.0.3",
        "ipv4_dst" : "10.0.0.2",
        "ip_proto" : 1,
        }
    ,"actions":[
        {"type":"OUTPUT","port": 3},
        
        ]}' http://localhost:8080/stats/flowentry/add		

echo
curl -X POST -d '{
    "dpid": 3,
    "cookie": 1,
    "cookie_mask": 1,
    "table_id": 0,"idle_timeout": 240,
    "priority": 11,
    "flags": 1,
    "match":{
        "in_port" : 1,
        "eth_type" : 2048,
        "ipv4_src":  "10.0.0.3",
        "ipv4_dst" : "10.0.0.1",
        "ip_proto" : 1,
        }
    ,"actions":[
        {"type":"OUTPUT","port": 3},
        
        ]}' http://localhost:8080/stats/flowentry/add		

echo
curl -X POST -d '{
    "dpid": 3,
    "cookie": 1,
    "cookie_mask": 1,
    "table_id": 0,"idle_timeout": 240,
    "priority": 11,
    "flags": 1,
    "match":{
        "in_port" : 1,
        "eth_type" : 2048,
        "ipv4_src":  "10.0.0.3",
        "ipv4_dst" : "10.0.0.4",
        "ip_proto" : 1,
        }
    ,"actions":[
        {"type":"OUTPUT","port": 3},
        
        ]}' http://localhost:8080/stats/flowentry/add		

echo
curl -X POST -d '{
    "dpid": 3,
    "cookie": 1,
    "cookie_mask": 1,
    "table_id": 0,"idle_timeout": 240,
    "priority": 11,
    "flags": 1,
    "match":{
        "in_port" : 2,
        "eth_type" : 2048,
        "ipv4_src":  "10.0.0.2",
        "ipv4_dst" : "10.0.0.4",
        "ip_proto" : 1,
        }
    ,"actions":[
        {"type":"OUTPUT","port": 3},
        
        ]}' http://localhost:8080/stats/flowentry/add		
		
echo
curl -X POST -d '{
    "dpid": 3,
    "cookie": 1,
    "cookie_mask": 1,
    "table_id": 0,"idle_timeout": 240,
    "priority": 11,
    "flags": 1,
    "match":{
        "in_port" : 2,
        "eth_type" : 2048,
        "ipv4_src":  "10.0.0.2",
        "ipv4_dst" : "10.0.0.1",
        "ip_proto" : 1,
        }
    ,"actions":[
        {"type":"OUTPUT","port": 3},
        
        ]}' http://localhost:8080/stats/flowentry/add		
		
echo
curl -X POST -d '{
    "dpid": 3,
    "cookie": 1,
    "cookie_mask": 1,
    "table_id": 0,"idle_timeout": 240,
    "priority": 11,
    "flags": 1,
    "match":{
        "in_port" : 2,
        "eth_type" : 2048,
        "ipv4_src":  "10.0.0.1",
        "ipv4_dst" : "10.0.0.4",
        "ip_proto" : 1,
        }
    ,"actions":[
        {"type":"OUTPUT","port": 3},
        
        ]}' http://localhost:8080/stats/flowentry/add						
		
		
echo --------------------------------------------------------

echo switch 4
echo
curl -X POST -d '{
    "dpid": 4,
    "cookie": 1,
    "cookie_mask": 1,
    "table_id": 0,"idle_timeout": 240,
    "priority": 11,
    "flags": 1,
    "match":{
        "in_port" : 2,
        "eth_type" : 2048,
        "ipv4_src":  "10.0.0.1",
        "ipv4_dst" : "10.0.0.4",
        "ip_proto" : 1,
        }
    ,"actions":[
        {"type":"OUTPUT","port": 1},
        
        ]}' http://localhost:8080/stats/flowentry/add
		
echo
curl -X POST -d '{
    "dpid": 4,
    "cookie": 1,
    "cookie_mask": 1,
    "table_id": 0,"idle_timeout": 240,
    "priority": 11,
    "flags": 1,
    "match":{
        "in_port" : 2,
        "eth_type" : 2048,
        "ipv4_src":  "10.0.0.3",
        "ipv4_dst" : "10.0.0.4",
        "ip_proto" : 1,
        }
    ,"actions":[
        {"type":"OUTPUT","port": 1},
        
        ]}' http://localhost:8080/stats/flowentry/add		

echo
curl -X POST -d '{
    "dpid": 4,
    "cookie": 1,
    "cookie_mask": 1,
    "table_id": 0,"idle_timeout": 240,
    "priority": 11,
    "flags": 1,
    "match":{
        "in_port" : 2,
        "eth_type" : 2048,
        "ipv4_src":  "10.0.0.2",
        "ipv4_dst" : "10.0.0.4",
        "ip_proto" : 1,
        }
    ,"actions":[
        {"type":"OUTPUT","port": 1},
        
        ]}' http://localhost:8080/stats/flowentry/add		
		
echo
curl -X POST -d '{
    "dpid": 4,
    "cookie": 1,
    "cookie_mask": 1,
    "table_id": 0,"idle_timeout": 240,
    "priority": 11,
    "flags": 1,
    "match":{
        "in_port" : 1,
        "eth_type" : 2048,
        "ipv4_src":  "10.0.0.4",
        "ipv4_dst" : "10.0.0.3",
        "ip_proto" : 1,
        }
    ,"actions":[
        {"type":"OUTPUT","port": 3},
        
        ]}' http://localhost:8080/stats/flowentry/add		

echo
curl -X POST -d '{
    "dpid": 4,
    "cookie": 1,
    "cookie_mask": 1,
    "table_id": 0,"idle_timeout": 240,
    "priority": 11,
    "flags": 1,
    "match":{
        "in_port" : 1,
        "eth_type" : 2048,
        "ipv4_src":  "10.0.0.4",
        "ipv4_dst" : "10.0.0.1",
        "ip_proto" : 1,
        }
    ,"actions":[
        {"type":"OUTPUT","port": 3},
        
        ]}' http://localhost:8080/stats/flowentry/add		

echo
curl -X POST -d '{
    "dpid": 4,
    "cookie": 1,
    "cookie_mask": 1,
    "table_id": 0,"idle_timeout": 240,
    "priority": 11,
    "flags": 1,
    "match":{
        "in_port" : 1,
        "eth_type" : 2048,
        "ipv4_src":  "10.0.0.4",
        "ipv4_dst" : "10.0.0.2",
        "ip_proto" : 1,
        }
    ,"actions":[
        {"type":"OUTPUT","port": 3},
        
        ]}' http://localhost:8080/stats/flowentry/add		

echo
curl -X POST -d '{
    "dpid": 4,
    "cookie": 1,
    "cookie_mask": 1,
    "table_id": 0,"idle_timeout": 240,
    "priority": 11,
    "flags": 1,
    "match":{
        "in_port" : 2,
        "eth_type" : 2048,
        "ipv4_src":  "10.0.0.3",
        "ipv4_dst" : "10.0.0.1",
        "ip_proto" : 1,
        }
    ,"actions":[
        {"type":"OUTPUT","port": 3},
        
        ]}' http://localhost:8080/stats/flowentry/add		
		
echo
curl -X POST -d '{
    "dpid": 4,
    "cookie": 1,
    "cookie_mask": 1,
    "table_id": 0,"idle_timeout": 240,
    "priority": 11,
    "flags": 1,
    "match":{
        "in_port" : 2,
        "eth_type" : 2048,
        "ipv4_src":  "10.0.0.3",
        "ipv4_dst" : "10.0.0.2",
        "ip_proto" : 1,
        }
    ,"actions":[
        {"type":"OUTPUT","port": 3},
        
        ]}' http://localhost:8080/stats/flowentry/add		
		
echo
curl -X POST -d '{
    "dpid": 4,
    "cookie": 1,
    "cookie_mask": 1,
    "table_id": 0,"idle_timeout": 240,
    "priority": 11,
    "flags": 1,
    "match":{
        "in_port" : 2,
        "eth_type" : 2048,
        "ipv4_src":  "10.0.0.2",
        "ipv4_dst" : "10.0.0.1",
        "ip_proto" : 1,
        }
    ,"actions":[
        {"type":"OUTPUT","port": 3},
        
        ]}' http://localhost:8080/stats/flowentry/add								