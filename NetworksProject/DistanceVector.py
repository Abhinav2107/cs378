from .Packet import *

class DistanceVector:

    infinity = 16
    period = 10

    def __init__(self, simulator, split_horizon, poison_reverse):
        self.simulator = simulator
        self.split_horizon = split_horizon
        self.poison_reverse = poison_reverse
        self.nodes = dict()
        self.count = 10

    def process_packet(self, packet):
        node = self.simulator.nodes[packet.link_dst]
        data = []
        for info in packet.data:
            # Check if new prefix or a lower cost path or update from the next hop
            if info[0] not in node.forwarding_table or info[1] < node.forwarding_table[info[0]][1] or node.forwarding_table[info[0]][0] == packet.link_src:
                    cost = node.neighbours[packet.link_src] + info[1]
                    if cost > DistanceVector.infinity and info[0] in node.forwarding_table:
                        node.forwarding_table.pop(info[0])
                    else:
                        node.forwarding_table[info[0]] = (packet.link_src, cost)
                        data.append((info[0], cost))

        # Send changed distance vectors to neighbours

        for neighbour, cost in node.neighbours.items():
            data_to_send = []
            for info in data:
                if node.forwarding_table[info[0]][0] == neighbour:  # Determine what to send to next hop based on split horizon and poison reverse settings
                    if self.split_horizon and self.poison_reverse:
                        data_to_send.append((info[0], DistanceVector.infinity))
                    elif not self.split_horizon:
                        data_to_send.append(info)
                else:
                        data_to_send.append(info)
            if len(data_to_send) > 0:
                packet = Packet("Node", "Node", node.name, neighbour, node.name, neighbour, "Distance Vector", cost+1, cost, data_to_send)
                self.simulator.put_packet(packet) 

    def poll_periodic_update(self):  
        self.count += 1
        if self.count >= DistanceVector.period:  # Check if it's time for a periodic update
            self.count = 0
            for name, node in self.simulator.nodes.items():
                for neighbour, cost in node.neighbours.items():
                    data = []
                    for ip_prefix, dv in node.forwarding_table.items():
                        if dv[0] == neighbour:
                            if self.split_horizon and self.poison_reverse:
                                data.append((ip_prefix, DistanceVector.infinity))
                            elif not self.split_horizon:
                                data.append((ip_prefix, dv[1]))
                        else:
                            data.append((ip_prefix, dv[1]))
                    if len(data) > 0:
                        packet = Packet("Node", "Node", name, neighbour, name, neighbour, "Distance Vector", cost+1, cost, data)
                        self.simulator.put_packet(packet)
    
    def update_connection(self, n1, n2, old_cost):
        if old_cost >= DistanceVector.infinity:
            return
        data = []
        node = self.simulator.nodes[n1]
        to_pop = []
        for ip_prefix, (next_hop, cost) in node.forwarding_table.items():  # Update costs based on link change
            if next_hop == n2:
                new_cost = cost + node.neighbours[n2] - old_cost
                node.forwarding_table[ip_prefix] = (next_hop, new_cost)
                if new_cost >= DistanceVector.infinity:
                    to_pop.append(ip_prefix)
                data.append((ip_prefix, new_cost))
        for ip_prefix in to_pop:  # Remove ip_prefixes with more than infinity costs
            node.forwarding_table.pop(ip_prefix)
        if node.neighbours[n2] >= DistanceVector.infinity:  # Destroy link if the new cost is over infinity
            node.neighbours.pop(n2)
        for neighbour, cost in node.neighbours.items():  # Send triggered update
            if neighbour != n2 or (not self.split_horizon):
                packet = Packet("Node", "Node", n1, neighbour, n1, neighbour, "Distance Vector", cost+1, cost, data)
                self.simulator.put_packet(packet)

