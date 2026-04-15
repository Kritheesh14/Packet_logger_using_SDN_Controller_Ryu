from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ipv4, tcp, udp, icmp, arp
from ryu.app.wsgi import WSGIApplication, ControllerBase, route
import json, time, threading
from collections import deque
from webob import Response

class PacketLoggerApp(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    _CONTEXTS = {'wsgi': WSGIApplication}

    def __init__(self, *args, **kwargs):
        super(PacketLoggerApp, self).__init__(*args, **kwargs)
        self.packet_log = deque(maxlen=100)
        self.counters = {"total":0, "TCP":0, "UDP":0, "ICMP":0, "ARP":0, "OTHER":0}
        self.lock = threading.Lock()
        wsgi = kwargs['wsgi']
        wsgi.register(PacketLoggerAPI, {'app': self})

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        dp = ev.msg.datapath
        parser = dp.ofproto_parser
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(dp.ofproto.OFPP_CONTROLLER, dp.ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(dp, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions):
        ofp = datapath.ofproto
        parser = datapath.ofproto_parser
        inst = [parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(datapath=datapath, priority=priority, match=match, instructions=inst)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
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

class PacketLoggerAPI(ControllerBase):
    def __init__(self, req, link, data, **cfg):
        super(PacketLoggerAPI, self).__init__(req, link, data, **cfg)
        self.app = data['app']

    @route('logger', '/stats', methods=['GET'])
    def get_stats(self, req, **kwargs):
        with self.app.lock:
            body = json.dumps({"stats": self.app.counters, "logs": list(self.app.packet_log)})
        return Response(content_type='application/json', body=body.encode(), 
                        headers={'Access-Control-Allow-Origin': '*'})

