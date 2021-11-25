#https://sourceforge.net/p/ryu/mailman/message/33237050/

#ADD FLOW ENTRY
#curl -X POST -d '{"dpid": 1,"cookie": 1,"cookie_mask": 1,"table_id": 0,"idle_timeout": 3000,"hard_timeout": 3000,"priority": 1,"flags": 1,"match":{"in_port": 1,"dl_dst": "00:00:00:00:00:02","dl_src": "00:00:00:00:00:01"},"actions":[{"type":"OUTPUT","port": 2}]}' http://localhost:8081/stats/flowentry/add



#ADD GROUP ENTRY
#TYPE SELECT , WATCH PORT IS 1
#curl -X POST -d '{"dpid": 1,"type": "SELECT","group_id": 1,"buckets": [{"watch_port": 1,"actions": [{"type": "OUTPUT","port": 1}]}]}' http://localhost:8080/stats/groupentry/add


#TYPE ANY , WATCH PORT IS ANY
#curl -X POST -d '{"dpid": 1,"type": "ANY","group_id": 2,"buckets": [{"actions": [{"type": "OUTPUT","port": 1}]}]}' http://localhost:8080/stats/groupentry/add


#TYPE SELECT , WATCH PORT IS 3 , TWO ACTIONS
curl -X POST -d '{"dpid": 1,"type": "SELECT","group_id": 30,"buckets": [{"WEIGHT":30,"watch_port": 3,"actions": [{"type": "OUTPUT","port": 1}]},{"WEIGHT":70,"watch_port": 3,"actions": [{"type": "OUTPUT","port": 2}]}]}' http://localhost:8080/stats/groupentry/add


#TYPE SELECT , WATCH PORT IS 3 , TWO ACTIONS
curl -X POST -d '{"dpid": 4,"type": "SELECT","group_id": 30,"buckets": [{"WEIGHT":30,"watch_port": 3,"actions": [{"type": "OUTPUT","port": 1}]},{"WEIGHT":70,"watch_port": 3,"actions": [{"type": "OUTPUT","port": 2}]}]}' http://localhost:8080/stats/groupentry/add

