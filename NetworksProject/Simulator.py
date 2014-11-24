from .Node import *
from .Host import *
from .Packet import *
from .DistanceVector import *
from .LinkState import *
import sys

class Simulator:

    # Constructor
    
    def __init__(self):
        self.packets = []
        self.new_packets = []
        self.next_packets = []
        self.nodes = dict()
        self.routing = None

    # Simulation Step

    def step(self):

        # Poll Periodic Routing Update

        if self.routing == "Link State":
            for node_name, node in self.nodes.items():
                node.routing.poll_periodic_update()
        else:    
            self.routing.poll_periodic_update()

        for node_name, node in self.nodes.items():
            for ip, host in node.hosts.items():
                host.poll_periodic_update()

        self.packets = self.packets + self.new_packets  # Add new packets to the packet list to be processed
        self.new_packets = []
        for packet in self.packets:
            if packet.ttl <= 0: # Discard packet if TTL expires
                continue
            packet.cost -= 1  # Subtract the remaning cost
            packet.ttl -= 1  # Subtract the remaining TTL
            if packet.cost <= 0:  # Deliver packet when cost hits 0
                if packet.link_dst in self.nodes:
                    self.nodes[packet.link_dst].process_packet(packet)
                elif packet.link_src in self.nodes and packet.link_dst in self.nodes[packet.link_src].hosts:
                    self.nodes[packet.link_src].hosts[packet.link_dst].process_packet(packet)
            else:
                self.next_packets.append(packet)  # Save undelivered packets for next step
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
        node = Node(self, name, position, ip_prefix)  # Create a new Node
        if self.routing == "Link State":
            node.routing = LinkState(self, node,self.link_state_refresh,self.link_state_refresh+5)  # Create a LinkState instance if required
        self.nodes[name] = node
        return node

    def remove_node(self, name):
        if name not in self.nodes:
            print("[ERROR] Invalid Node", file=sys.stderr)
            return
        for neighbour in list(self.nodes[name].neighbours.keys()):
            self.update_connection(name, neighbour, float("+inf"))
        self.nodes.pop(name)

    def add_host(self, ip, node, position):
        if node not in self.nodes:
            print("[ERROR] Invalid Node", file=sys.stderr)
        elif not prefix_match(ip, self.nodes[node].ip_prefix):
            print("[ERROR] Invalid IP for this prefix", file=sys.stderr)
        elif ip in self.nodes[node].hosts:
            print("[ERROR] IP already exists", file=sys.stderr)
            return self.nodes[node].hosts[ip]
        else:
            host = Host(self, ip, node, position)  # Create a new Host
            self.nodes[node].add_host(host)  # Add Host to the Node
            return host
        return None

    def remove_host(self, ip, node):
        if node not in self.nodes:
            print("[ERROR] Invalid Node", file=sys.stderr)
        elif ip not in self.nodes[node].hosts:
            print("[ERROR] Invalid IP", file=sys.stderr)
        else:
            self.nodes[node].remove_host(ip)
    
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
            self.routing = DistanceVector(self, protocol[1], protocol[2],protocol[3])  # Create a shared DistanceVector instance
        elif protocol[0] == "Link State":
            self.routing = "Link State"
            self.link_state_refresh = protocol[1]
        else:
            print("[ERROR] Invalid Routing Protocol",file=sys.stderr)

    def error(self, node, msg, packet):
        if packet.protocol == "ICMP":  # ICMPs cannot generate ICMPs to avoid infinite loop
            return
        data = (msg, packet)
        icmp = Packet("Node", packet.src_type, node.name, packet.src, None, None, "ICMP", 64, None, data)
        node.process_packet(icmp) 
