from Packet import *

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
            if info[0] not in node.forwarding_table or info[1] < node.forwarding_table[info[0]][1] or (node.forwarding_table[info[0]][0] == packet.link_src and node.forwarding_table[info[0]][1] > node.neighbours[packet.link_src] + info[1]):
                    cost = node.neighbours[packet.link_src] + info[1]
                    if cost > DistanceVector.infinity:
                        node.forwarding_table.pop(info[0])
                    else:
                        node.forwarding_table[info[0]] = (packet.link_src, cost)
                        data.append((info[0], cost))

        for neighbour, cost in node.neighbours.items():
            data_to_send = []
            for info in data:
                if node.forwarding_table[info[0]][0] == neighbour:
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
        if self.count >= DistanceVector.period:
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
            
