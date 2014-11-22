from Node import *
from Host import *
from Packet import *
from DistanceVector import *
from LinkState import *
import sys

class Simulator:
    
    def __init__(self):
        self.packets = []
        self.new_packets = []
        self.next_packets = []
        self.nodes = dict()
        self.routing = None

    def step(self):
        if self.routing == "Link State":
            for node_name, node in self.nodes.items():
                node.routing.poll_periodic_update()
        else:    
            self.routing.poll_periodic_update()
        self.packets = self.packets + self.new_packets
        self.new_packets = []
        for packet in self.packets:
            if packet.ttl <= 0:
                continue
            packet.cost -= 1
            packet.ttl -= 1
            if packet.cost <= 0:
                if packet.link_dst in self.nodes:
                    self.nodes[packet.link_dst].process_packet(packet)
                elif packet.link_src in self.nodes and packet.link_dst in self.nodes[packet.link_src].hosts:
                    self.nodes[packet.link_src].hosts[packet.link_dst].process_packet(packet)
            else:
                self.next_packets.append(packet)
        self.packets = self.next_packets
        self.next_packets = []

    def put_packet(self, packet):
        self.new_packets.append(packet)

    def add_node(self, name, position, ip_prefix):
        if self.routing is None:
            print("[ERROR] Set routing protocol before adding nodes", file=sys.stderr)
            return None 
        if name in self.nodes:
            print("[ERROR] Node already exists", file=sys.stderr)
            return self.nodes[name]
        node = Node(self, name, position, ip_prefix)
        if self.routing == "Link State":
            node.routing = LinkState(self, node)
        self.nodes[name] = node
        return node

    def add_host(self, ip, node, position):
        if node in self.nodes and prefix_match(ip, self.nodes[node].ip_prefix):
            host = Host(self, ip, node, position)
            self.nodes[node].add_host(host)
            return host
        print("[ERROR] Invalid Node or IP", file=sys.stderr)
        return None
    
    def add_connection(self, n1, n2, cost):
        self.update_connection(n1, n2, cost)

    def update_connection(self, n1, n2, cost):
        if n1 not in self.nodes or n2 not in self.nodes:
            print("[ERROR] Invalid Node(s)", file=sys.stderr)
            return
        self.nodes[n1].update_connection(n2, cost)
        self.nodes[n2].update_connection(n1, cost)

    def set_routing_protocol(self, protocol):
        if protocol[0] == "Distance Vector":
            self.routing = DistanceVector(self, protocol[1], protocol[2])
        if protocol[0] == "Link State":
            self.routing = "Link State"

    def error(self, node, msg, packet):
        if packet.protocol == "ICMP":
            return
        data = (msg, packet)
        icmp = Packet("Node", packet.src_type, node.name, packet.src, None, None, "ICMP", 64, None, data)
        node.process_packet(icmp) 
