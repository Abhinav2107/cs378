from node import *
from distance_vector import *
from protocols import *
import math

class simulator:
	node_count = 0
	node_set = {}
	connection_count = 0
	connection_set = {}
	packet_list = []
	clock = 0
	clock_step = 0.1
	processor = protocols()

	def __init__(self):
		node_count = 0

	def initialise(self,duration):
		for time_clock in range(0,math.floor(duration/self.clock_step)):
			new_packet_list = []
			for packets in self.packet_list:
				if(packets.update_packet() == 0):
					what_to_send = self.processor.get_protocol(packets.protocol).process_packet(self.node_set[packets.destination_node],packets)
					n_packet_list = self.processor.get_protocol(packets.protocol).create_packets(self.node_set[packets.destination_node],self.connection_set,what_to_send)
					new_packet_list = new_packet_list + n_packet_list

			for keys, values in self.node_set.items():
				n_packet_list = self.processor.get_protocol(2).create_packets(values,self.connection_set,values.update_node())
				new_packet_list = new_packet_list + n_packet_list

			self.packet_list[:] = [x for  x in self.packet_list if x.count_down_to_reach > 0]
			self.packet_list = self.packet_list + new_packet_list

			print("\n" + str(time_clock))
			for packets in self.packet_list:
				packets.packet_print()

	def get_coordinate(self,id):
		return [0,0]

	def add_node(self,node_name):
		self.node_count += 1
		new_node = node(self.node_count,
			node_name,
			self.get_coordinate(self.node_count))
		self.node_set[node_name] = new_node

	def add_connection(self,node1,node2,distance):
		if(node1 in self.node_set.keys() and node2 in self.node_set.keys()):
			self.connection_count += 1
			new_connection = connection(self.connection_count,
				[node1,node2],
				distance,
				self.clock_step)
			self.connection_set[(node1,node2)] = new_connection
			self.connection_set[(node2,node1)] = new_connection
			self.node_set[node1].add_connection(node2,distance)
			self.node_set[node2].add_connection(node1,distance)
		else:
			print("Invalid Connection")

	def get_routing_tables(self):
		for keys,nodes in self.node_set.items():
			print(nodes.name + " : " + str(nodes.forwarding_table))

sim = simulator()
sim.add_node("n0")
sim.add_node("n1")
sim.add_node("n2")
sim.add_node("n3")
sim.add_connection("n0","n1",1)
sim.add_connection("n0","n2",3)
sim.add_connection("n1","n2",1)
sim.add_connection("n2","n3",1)
sim.initialise(10)
sim.get_routing_tables()