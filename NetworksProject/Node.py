def prefix_match(ip, ip_prefix):  # Check if IP matches the prefix
    if ip_prefix == None:
        return False
    ip_prefix = ip_prefix.split("/")
    if ip_mask_to_network(ip_prefix[0], ip_prefix[1]) == ip_mask_to_network(ip, ip_prefix[1]):
        return True
    return False


def ip_mask_to_network(ip, mask):  # Get network bits from IP and mask
    ip_parts = [int(_) for _ in ip.split(".")]
    binary = ""
    for part in ip_parts:  # Convert each byte of IP to 0s and 1s
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
        self.routing.update_connection(self.name, node_name, old_cost)  # Trigger Routing Update

    def add_host(self, host):
        self.hosts[host.ip] = host

    def remove_host(self, ip):
        self.hosts.pop(ip)
    
    def process_packet(self, packet):
        if packet.dst_type == "Node" and packet.dst == self.name and packet.link_src in self.neighbours:  # Packet intended for this Node
            print(self.name + " Received " + packet.protocol + " Packet from " + packet.src)
            if packet.protocol == "Distance Vector" or packet.protocol == "Link State":  # Let the routing instance handle routing packets
                self.routing.process_packet(packet)

        elif packet.dst_type == "Host":
            if packet.dst in self.hosts:  # Deliver if my host
                self.deliver(packet)
            elif not prefix_match(packet.dst, self.ip_prefix):  # Forward if IP doesn't match my prefix    
                self.forward(packet)
            else:  # My network but invalid host
                self.simulator.error(self, "Host Unreachable", packet)  # Generate an ICMP message

    def deliver(self, packet):
        packet.link_src = self.name
        packet.link_dst = packet.dst
        packet.cost = 1
        if packet.ttl < packet.cost:  # If TTL is less than cost, packet cannot reach
            self.simulator.error(self, "TTL Expired in Transit", packet)  # Generate an ICMP message
        else:
            print(self.name + " Delivering Packet to " + packet.dst)
            self.simulator.put_packet(packet)

    def forward(self, packet):
        for ip_prefix in self.forwarding_table:  # Match prefix in the forwarding table
            if prefix_match(packet.dst, ip_prefix):
                packet.link_src = self.name
                packet.link_dst = self.forwarding_table[ip_prefix][0]
                packet.cost = self.neighbours[packet.link_dst]
                if packet.ttl < packet.cost:  # Validate TTL
                    self.simulator.error(self, "TTL Expired in Transit", packet)
                else:
                    print(self.name + " Forwarding Packet for " + packet.dst + " to " + packet.link_dst)
                    self.simulator.put_packet(packet)
                return
        self.simulator.error(self, "Network Unreachable", packet)  # Generate an ICMP message if no ip_prefix matches
