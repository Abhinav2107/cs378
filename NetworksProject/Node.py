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
        self.routing = simulator.routing

    def update_connection(self, node_name, cost):
        if node_name not in self.neighbours:
            old_cost = float("+inf")
        else:
            old_cost = self.neighbours[node_name]
        self.neighbours[node_name] = cost
        self.routing.update_connection(self.name, node_name, old_cost)

    def add_host(self, host):
        self.hosts[host.ip] = host

    def process_packet(self, packet):
        if packet.dst_type == "Node" and packet.dst == self.name and packet.link_src in self.neighbours:
            print(self.name + " Received " + packet.protocol + " Packet from " + packet.src)
            if packet.protocol == "Distance Vector" or packet.protocol == "Link State":
                self.routing.process_packet(packet)

        elif packet.dst_type == "Host":
            if packet.dst in self.hosts:
                self.deliver(packet)
            elif not prefix_match(packet.dst, self.ip_prefix):    
                self.forward(packet)
            else:
                self.simulator.error(self, "Host Unreachable", packet)

    def deliver(self, packet):
        packet.link_src = self.name
        packet.link_dst = packet.dst
        packet.cost = 1
        if packet.ttl < packet.cost:
            self.simulator.error(self, "TTL Expired in Transit", packet)
        else:
            print(self.name + " Delivering Packet to " + packet.dst)
            self.simulator.put_packet(packet)

    def forward(self, packet):
        for ip_prefix in self.forwarding_table:
            if prefix_match(packet.dst, ip_prefix):
                packet.link_src = self.name
                packet.link_dst = self.forwarding_table[ip_prefix][0]
                packet.cost = self.neighbours[packet.link_dst]
                if packet.ttl < packet.cost:
                    self.simulator.error(self, "TTL Expired in Transit", packet)
                else:
                    print(self.name + " Forwarding Packet for " + packet.dst + " to " + packet.link_dst)
                    self.simulator.put_packet(packet)
                return
        self.simulator.error(self, "Network Unreachable", packet)
