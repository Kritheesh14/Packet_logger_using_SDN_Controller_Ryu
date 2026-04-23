from ryu.base import app_manager #like the main() function - handles app cycle - loading, starting, closing
from ryu.controller import ofp_event # allows code to listen to network responds, like packet arrival/switch connections
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, set_ev_cls #represent states of switch , config - when switch first connects, main - normal execution of network operations
from ryu.ofproto import ofproto_v1_3 #specifies we are using openflow version 1.3 - contains command codes and constants for switches 
from ryu.lib.packet import packet, ethernet, ipv4, tcp, udp, icmp, arp 
from ryu.app.wsgi import WSGIApplication, ControllerBase, route # WSGI - built in web server inside ryu- allows controller to be web host, other two allow to create URL paths
import json, time, threading #and lock - since web API and packet logger work at the same time - counters might be touched at the same time - lock prevents crashing by waiting for their turn
from collections import deque #deque - allows us to keep only the last 100 packets
from webob import Response


#Network logic

class PacketLoggerApp(app_manager.RyuApp): # workhorse class - builds all the required frameworks and interacts with the network hardware
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION] 
    _CONTEXTS = {'wsgi': WSGIApplication} #WSGI - web server gateway interface

    def __init__(self, *args, **kwargs):
        super(PacketLoggerApp, self).__init__(*args, **kwargs) #used by the ryu framework, to set up shared ememory ie logs and counters
        self.packet_log = deque(maxlen=100)
        self.counters = {"total":0, "TCP":0, "UDP":0, "ICMP":0, "ARP":0, "OTHER":0}
        self.lock = threading.Lock()
        wsgi = kwargs['wsgi']
        wsgi.register(PacketLoggerAPI, {'app': self})

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev): #triggered by the switch - thru an openflow 'features reply' message - happens as soon as switch-controller handshake is complete
        dp = ev.msg.datapath
        parser = dp.ofproto_parser
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(dp.ofproto.OFPP_CONTROLLER, dp.ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(dp, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions): #utility function- used by others to write rules into switch hardware
        ofp = datapath.ofproto
        parser = datapath.ofproto_parser
        inst = [parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(datapath=datapath, priority=priority, match=match, instructions=inst)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev): #triggered by switch everytime a packet misses the flow table - busiest function - runs thousands of times during an iperf test
        msg = ev.msg
        dp = msg.datapath
        ofp = dp.ofproto
        parser = dp.ofproto_parser
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)
        if not eth: return

        # Protocol Detection Logic
        proto = "OTHER"
        if pkt.get_protocol(tcp.tcp): proto = "TCP"
        elif pkt.get_protocol(udp.udp): proto = "UDP"
        elif pkt.get_protocol(icmp.icmp): proto = "ICMP"
        elif pkt.get_protocol(arp.arp): proto = "ARP"

        with self.lock:
            self.counters["total"] += 1
            self.counters[proto] += 1
            self.packet_log.appendleft({
                "ts": time.strftime("%H:%M:%S"),
                "proto": proto,
                "src": eth.src,
                "dst": eth.dst
            })

        # Forwarding Logic: Tell switch to Flood the packet so ping works
        actions = [parser.OFPActionOutput(ofp.OFPP_FLOOD)]
        out = parser.OFPPacketOut(datapath=dp, buffer_id=msg.buffer_id,
                                  in_port=msg.match['in_port'], 
                                  actions=actions, data=msg.data)
        dp.send_msg(out)


#Data Delivery 
class PacketLoggerAPI(ControllerBase): #The messenger function - controller base; no switch/packet data - only creates conversation with the browser
    def __init__(self, req, link, data, **cfg): #used by Wsgi, this gives access of the packetloggerapp class to the api
        super(PacketLoggerAPI, self).__init__(req, link, data, **cfg)
        self.app = data['app']

    @route('logger', '/stats', methods=['GET'])
    def get_stats(self, req, **kwargs): #triggered by the web dashboard- every 2 seconds, the dashboard sends a HTTP GET request to stats
        with self.app.lock:
            body = json.dumps({"stats": self.app.counters, "logs": list(self.app.packet_log)})
        return Response(content_type='application/json', body=body.encode(), 
                        headers={'Access-Control-Allow-Origin': '*'})
