from Node import *
from Host import *
from Packet import *
from DistanceVector import *

class Simulator:
    
    def __init__(self):
        self.packets = []
        self.new_packets = []
        self.next_packets = []
        self.nodes = dict()
        self.routing = None

    def step(self):
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
        node = Node(self, name, position, ip_prefix)
        self.nodes[name] = node
        return node

    def add_host(self, ip, node, position):
        if node in self.nodes and prefix_match(ip, self.nodes[node].ip_prefix):
            host = Host(self, ip, node, position)
            self.nodes[node].add_host(host)
            return host
        return None
    
    def add_connection(self, n1, n2, cost):
        self.nodes[n1].add_connection(n2, cost)
        self.nodes[n2].add_connection(n1, cost) 

    def set_routing_protocol(self, protocol):
        if protocol[0] == "Distance Vector":
            self.routing = DistanceVector(self, protocol[1], protocol[2])
