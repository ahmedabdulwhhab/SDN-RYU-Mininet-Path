The aim of this project is to detect links either added or removed. Then apply possible path, no conditions for this path.
<br>
Use events
<br>

    @set_ev_cls(event.EventSwitchEnter) #update datapath_list[dpid], o/p is self.datapath_list[switch.id]
<br>

    @set_ev_cls(event.EventSwitchLeave, MAIN_DISPATCHER) #del datapath_list[dpid], del adjacency
<br>

    @set_ev_cls(event.EventLinkAdd, MAIN_DISPATCHER) #create self.adjacency
<br>
    @set_ev_cls(event.EventLinkDelete, MAIN_DISPATCHER) #delete some links in self.adjacency
<br>
self.adjacency contains all available links like command net in mininet.
<br>
use this link for more information 
<br>
https://youtu.be/rpUijnQOlU8
