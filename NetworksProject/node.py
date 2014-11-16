def prefix_match(ip, ip_prefix):
    if ip_prefix == None:
        return False
    ip_prefix = ip_prefix.split("/")
    if ip_mask_to_network(ip_prefix[0], ip_prefix[1]) == ip_mask_to_network(ip, ip_prefix[1]):
        return True
    return False


def ip_mask_to_network(ip, mask):
    ip_parts = [int(_) for _ in ip.split(".")]
    binary = ""
    for part in ip_parts:
        b = bin(part)[2:]
        binary += "0"*(8-len(b))
        binary += b
    return binary[:int(mask)]

class Node:

    processing_time = 0
    max_update_limit = 1000

    def __init__(self,simulator,name,position,ip_prefix):
        self.simulator = simulator
        self.name = name
        self.position = position
        self.forwarding_table = dict()
        self.forwarding_table[ip_prefix] = (name, 0)
        self.count_to_update = 0
        self.neighbours = {}
        self.hosts = dict()
        self.ip_prefix = ip_prefix

    def add_connection(self,node_name,cost):
        self.neighbours[node_name] = cost
        if self.simulator.nodes[node_name].ip_prefix is not None:
            self.forwarding_table[self.simulator.nodes[node_name].ip_prefix] = (node_name, cost)

    def add_host(self, host):
        self.hosts[host.ip] = host

    def process_packet(self, packet):
        if packet.dst_type == "Node" and packet.dst == self.name:
            print(self.name + " Received Packet from " + packet.src)
            if packet.protocol == "Distance Vector":
                self.simulator.routing.process_packet(packet)

        elif packet.dst_type == "Host":
            if packet.dst in self.hosts:
                self.deliver(packet)
            elif not prefix_match(packet.dst, self.ip_prefix):    
                self.forward(packet)

    def deliver(self, packet):
        packet.link_src = self.name
        packet.link_dst = packet.dst
        packet.cost = 1
        print(self.name + " Delivering Packet to " + packet.dst)
        self.simulator.put_packet(packet)

    def forward(self, packet):
        for ip_prefix in self.forwarding_table:
            if prefix_match(packet.dst, ip_prefix):
                packet.link_src = self.name
                packet.link_dst = self.forwarding_table[ip_prefix][0]
                packet.cost = self.neighbours[packet.link_dst]
                print(self.name + " Forwarding Packet for " + packet.dst + " to " + packet.link_dst)
                self.simulator.put_packet(packet)
                return

