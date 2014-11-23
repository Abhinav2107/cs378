from .Packet import *
import copy
import heapq

class LinkState:
    max_timeout = 11    # the timeout value for the link state entries
    infinity = 16
    period = 10

    def __init__(self, simulator, node):
        self.node = node
        self.simulator = simulator
        self.nodes = dict()                 # the adjacency list for the graph along with link costs
        self.nodes[self.node.name] = dict() 
        self.timeout = dict()               # current values of link state timers
        self.sequence = dict()              # sequence number of last received link state
        self.count = 10
        self.sequence_number = 0

    def check(self, packet):
        to_pop = []
        for neighbour in self.nodes[packet.src]:
            if neighbour not in packet.data[2]:
                to_pop.append(neighbour)
        for neighbour in to_pop:        
            self.nodes[packet.src].pop(neighbour)
            self.nodes[neighbour].pop(packet.src)

        for neighbour, cost in packet.data[2].items():
            if neighbour not in self.nodes:
                self.nodes[neighbour] = dict()
                self.timeout[neighbour] = LinkState.max_timeout
                self.sequence[neighbour] = 0

            self.nodes[neighbour][packet.src] = cost
            self.nodes[packet.src][neighbour] = cost

    def forward(self, packet):
        for neighbour, cost in self.node.neighbours.items():
            if neighbour != packet.link_src:
                new_packet = copy.copy(packet)
                new_packet.dst = None
                new_packet.link_src = self.node.name
                new_packet.link_dst = neighbour
                new_packet.ttl -= 1
                new_packet.cost =  cost
                self.simulator.put_packet(new_packet)

    def process_packet(self, packet):
        if packet.src == self.node.name:                        # discard packet to self
            return
        if packet.src not in self.nodes:                        # discover new node in graph
            self.nodes[packet.src] = dict()
            self.timeout[packet.src] = LinkState.max_timeout
            self.sequence[packet.src] = packet.data[0]
            self.check(packet)
            self.forward(packet)

        elif packet.data[0] > self.sequence[packet.src]:        # retransmission from known node
            self.timeout[packet.src] = LinkState.max_timeout
            self.sequence[packet.src] = packet.data[0]

            if packet.data[1] != 'p':                           # use the new link state given by triggered update 
                self.check(packet)

            self.forward(packet)                                # forward packet to neighbours

    
##############################################################
# This function is called by the simulator on each time step #
##############################################################
    def poll_periodic_update(self):
        to_pop = []

        for neighbour in self.timeout:
            self.timeout[neighbour] -= 1                        # decrement timer values for link state entries

            if self.timeout[neighbour] == 0:
                self.sequence.pop(neighbour)                    # remove expired entries

                for n in self.nodes[neighbour].keys():
                    #print(n+neighbour)
                    self.nodes[n].pop(neighbour)

                self.nodes.pop(neighbour)
                to_pop.append(neighbour)

        for neighbour in to_pop:
            self.timeout.pop(neighbour)

        self.count += 1                                         # maintain count from last periodic update
        if self.count >= LinkState.period:
            self.count = 0 
            #self.graph()
            self.sequence_number += 1
            data = (self.sequence_number, 'p', self.node.neighbours)

            for neighbour, cost in self.node.neighbours.items():
                packet = Packet("Node", "Node", self.node.name, None, self.node.name, neighbour, "Link State", 64, cost, data)
                self.simulator.put_packet(packet)               # send periodic update after LinkState.period time steps

        self.dijkstra()                                         # recompute the shortest distances and the routing table


#############################################################################################
# This function is called by the simulator whenever a link is created, destroyed or changed #
#############################################################################################        
    def update_connection(self, n1, n2, old_cost):
        if n1 == n2:
            return
        if old_cost > LinkState.infinity:                       # new link created
            self.nodes[n1][n2] = self.node.neighbours[n2]       # update link state
            self.nodes[n2] = dict()
            self.nodes[n2][n1] = self.node.neighbours[n2]
            self.sequence[n2] = 0

        elif self.node.neighbours[n2] > LinkState.infinity:     # link destroyed
            self.node.neighbours.pop(n2)                        # remove n2 from list of neighbours of n1
            
            if n2 in self.nodes[n1]:                            # update link state
                self.nodes[n1].pop(n2)
                self.nodes[n2].pop(n1)

        else:
            self.nodes[n1][n2] = self.node.neighbours[n2]       # update link state
            self.nodes[n2][n1] = self.node.neighbours[n2]

        self.sequence_number += 1
        data = (self.sequence_number, 't', self.node.neighbours)

        for neighbour, cost in self.node.neighbours.items():    # send triggered update to neighbours
            #print("Sending to" + neighbour)
            packet = Packet("Node", "Node", self.node.name, None, self.node.name, neighbour, "Link State", 64, cost, data)
            self.simulator.put_packet(packet)

        self.dijkstra()                                         # recompute the shortest distances and the routing table

    def graph(self):
        print(self.nodes)

    
#############################################################################################
# This function recomputes the shortest distance and next hop to each node in the graph by  #
# running Dijkstra's algorithm. Then it updates the routing table entries                   #
#############################################################################################        
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
        next_hop[self.node.name] = self.node.name
        unvisited[self.node.name] = False
        remaining -= 1
        curr = self.node.name

        while tentative[curr] != float("inf") and remaining > 0:
            for neighbour in self.nodes[curr]:
                if tentative[neighbour] > tentative[curr] + self.nodes[curr][neighbour]:
                    tentative[neighbour] = tentative[curr] + self.nodes[curr][neighbour]
                    if curr == self.node.name:
                        next_hop[neighbour] = neighbour
                    else:
                        next_hop[neighbour] = next_hop[curr]

            unvisited[curr] = False
            temp_c = float("inf")

            for neighbour, cost in tentative.items():
                if cost < temp_c and unvisited[neighbour]:
                    curr = neighbour
                    temp_c = cost

            remaining -= 1
        
        new_forwarding_table = dict()
        for name, next in next_hop.items():
            if tentative[name] != float("inf"):
                new_forwarding_table[self.simulator.nodes[name].ip_prefix] = (next, tentative[name])

        self.node.forwarding_table = new_forwarding_table       # update routing table for the node under consideration
