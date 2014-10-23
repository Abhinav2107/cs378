from node import *
from packet import *

class distance_vector:
	def __init__(self):
		inti = 1

	def process_packet(self,forwarding_table,packet):
		print("process_packet")
		update_list = []
		for keys, values in packet.information.items():
			if(keys in forwarding_table):
				if(forwarding_table[keys][0] >= 1+values):
					forwarding_table[keys] = [1+values,packet.source_node]	
					update_list.append(keys)
			else:
				forwarding_table[keys] = [1+values,packet.source_node]
				update_list.append(keys)
		return update_list

	def create_packets(self,node_obj,connection_table,what_to_send):
		print("create_packets" + str(len(what_to_send)))
		send_this = {}
		for send in what_to_send:
			send_this[send] = node_obj.forwarding_table[send][0]
		if(send_this == {}):
			return []
		packet_list = []
		for keys in node_obj.neighbours:
			pck = packet(node_obj.name,keys,1,send_this)
			pck.set_count_down(connection_table[(node_obj.name,keys)])
			packet_list.append(pck)
		print("creating_packets " + str(len(packet_list)))
		return packet_list