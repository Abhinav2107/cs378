from node import *
from packet import *

class distance_vector:
	infinity = 16
	def __init__(self,features):
		self.split_horizon = 0
		self.poison_reverse = 0
		self.protocol = features
		if(features == 2 or features == 3):
			self.split_horizon = 1
		if(features == 3):
			self.poison_reverse = 1

	def process_packet(self,node,packet):
		update_list = []
		for keys, values in packet.information.items():
			if(node.name == packet.source_node):
				continue
			new_value = values + node.neighbours[packet.source_node]
			if(keys in node.forwarding_table):
				if(node.forwarding_table[keys][0] >= new_value):
					node.forwarding_table[keys] = [new_value,packet.source_node]	
					update_list.append(keys)
			else:
				node.forwarding_table[keys] = [new_value,packet.source_node]
				update_list.append(keys)
		return [packet.source_node, update_list]

	def create_packets(self,node_obj,connection_table,what_to_send):
		send_this = {}
		for send in what_to_send[1]:
			send_this[send] = node_obj.forwarding_table[send][0]
		if(send_this == {}):
			return []
		packet_list = []
		for keys in node_obj.neighbours.keys():
			if(keys == what_to_send[0]):
				if(self.split_horizon == 1 and self.poison_reverse == 0):
					continue
				elif(self.split_horizon == 1 and self.poison_reverse == 0):
					duplicate_send_this = send_this
					for keys in duplicate_send_this:
						duplicate_send_this[keys] = infinity
					pck = packet(node_obj.name,keys,self.protocol,duplicate_send_this)
					pck.set_count_down(connection_table[(node_obj.name,keys)])
					packet_list.append(pck)
					continue
			pck = packet(node_obj.name,keys,self.protocol,send_this)
			pck.set_count_down(connection_table[(node_obj.name,keys)])
			packet_list.append(pck)
		return packet_list