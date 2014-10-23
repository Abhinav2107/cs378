from node import *
from packet import *

class distance_vector:

	def __init__(self):
		inti = 1

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
		return update_list

	def create_packets(self,node_obj,connection_table,what_to_send):
		send_this = {}
		for send in what_to_send:
			send_this[send] = node_obj.forwarding_table[send][0]
		if(send_this == {}):
			return []
		packet_list = []
		for keys in node_obj.neighbours.keys():
			pck = packet(node_obj.name,keys,1,send_this)
			pck.set_count_down(connection_table[(node_obj.name,keys)])
			packet_list.append(pck)
		return packet_list