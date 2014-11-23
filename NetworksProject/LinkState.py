from .Packet import *
import copy
import heapq

class LinkState:
    max_timeout = 10
    infinity = 16
    period = 10

    def __init__(self, simulator, node):
        self.node = node
        self.simulator = simulator
        self.nodes = dict()
        self.nodes[self.node.name] = dict()
        self.timeout = dict()
        self.sequence = dict()
        self.count = 10
        self.sequence_number = 0

    def check(self, packet):
        to_pop = []
        for neighbour in self.nodes[packet.link_src]:
            if neighbour not in packet.data[2]:
                to_pop.append(neighbour)
        for neighbour in to_pop:        
            self.nodes[packet.link_src].pop(neighbour)
            self.nodes[neighbour].pop(packet.link_src)

        for neighbour, cost in packet.data[2].items():
            if neighbour not in self.nodes:
                self.nodes[neighbour] = dict()
                self.timeout[neighbour] = LinkState.max_timeout
                self.sequence[neighbour] = 0

            self.nodes[neighbour][packet.link_src] = cost
            self.nodes[packet.link_src][neighbour] = cost

    def forward(self, packet):
        for neighbour, cost in self.node.neighbours.items():
            if neighbour != packet.link_src:
                new_packet = copy.copy(packet)
                new_packet.link_src = self.node.name
                new_packet.link_dst = neighbour
                new_packet.ttl -= 1
                new_packet.cost =  cost
                self.simulator.put_packet(new_packet)

    def process_packet(self, packet):
        if packet.src not in self.nodes:
            self.nodes[packet.src] = dict()
            self.timeout[packet.src] = LinkState.max_timeout
            self.sequence[packet.src] = packet.data[0]
            self.check(packet)
            self.forward()

        elif packet.data[0] > self.sequence[packet.src]:
            self.timeout[packet.src] = LinkState.max_timeout
            self.sequence[packet.src] = packet.data[0]

            if packet.data[1] != 'p':
                check(packet)

            forward(packet)

    def poll_periodic_update(self):
        to_pop = []

        for neighbour in self.timeout:
            self.timeout[neighbour] -= 1

            if self.timeout[neighbour] == 0:
                self.sequence.pop(neighbour)

                for n in self.nodes[neighbour]:
                    self.nodes[n].pop(neighbour)

                self.nodes.pop(neighbour)
                to_pop.append(neighbour)

        for neighbour in to_pop:
            self.timeout.pop(neighbour)

        self.count += 1
        if self.count >= LinkState.period:
            self.count = 0 
            self.graph()
            self.sequence_number += 1
            data = (self.sequence_number, 'p', self.node.neighbours)

            for neighbour, cost in self.node.neighbours.items():
                packet = Packet("Node", "Node", self.node.name, neighbour, self.node.name, neighbour, "Link State", cost+1, cost, data)
                self.simulator.put_packet(packet)

        dijkstra()
        
    def update_connection(self, n1, n2, old_cost):
        if old_cost > LinkState.infinity:
            self.nodes[n1][n2] = self.node.neighbours[n2]
            self.nodes[n2] = dict()
            self.nodes[n2][n1] = self.node.neighbours[n2]

        elif self.node.neighbours[n2] > LinkState.infinity:
            self.node.neighbours.pop(n2)
            
            if n2 in self.nodes[n1]:
                self.nodes[n1].pop(n2)
                self.nodes[n2].pop(n1)

        else:
            self.nodes[n1][n2] = self.node.neighbours[n2]
            self.nodes[n2][n1] = self.node.neighbours[n2]

        self.sequence_number += 1
        data = (self.sequence_number, 't', self.node.neighbours)

        for neighbour, cost in self.node.neighbours.items():
            if neighbour != n2:
                packet = Packet("Node", "Node", self.node.name, neighbour, self.node.name, neighbour, "Link State", cost+1, cost, data)
                self.simulator.put_packet(packet)

        dijkstra()

    def graph(self):
        print(self.nodes)

    

    def dijkstra(self):
        unvisited = dict()
        tentative = dict()
        next_hop = dict()
        remaining = 0
        for node in self.nodes:
            tentative[node] = float("inf")
            next_hop[node] = ""
            unvisited[node] = True
            remaining += 1

        tentative[self.node.name] = 0
        next_hop[self.node.name] = "localhost"
        unvisited[self.node.name] = False
        remaining -= 1
        curr = self.node.name

        while tentative[curr] != float("inf") and remaining > 0:
            for neighbour in self.nodes[curr]:
                if tentative[neighbour] > tentative[curr] + self.nodes[curr][neighbour]:
                    tentative[neighbour] = tentative[curr] + self.nodes[curr][neighbour]
                    next_hop[neighbour] = curr

            unvisited[curr] = False
            temp_c = float("inf")

            for neighbour, cost in tentative.items():
                if cost < temp_c and unvisited[neighbour]:
                    curr = neighbour
                    temp_c = cost

            remaining -= 1
        
        new_forwarding_table = dict()
        for name, next in next_hop.items():
            new_forwarding_table[self.simulator.nodes[name].prefix] = (next, tentative[name])

        self.node.forwarding_table = new_forwarding_table

        print(next_hop)