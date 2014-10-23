from node import *
import math

class packet:

	def __init__(self,src,dst,protocol,info):
		self.source_node = src
		self.destination_node = dst
		self.protocol = protocol
		self.information = {}
		self.information = info
		self.count_down_to_reach = 0

	def set_count_down(self,connection):
		self.count_down_to_reach = math.floor(connection.distance/connection.clock_step)

	def update_packet(self):
		self.count_down_to_reach -= 1
		return self.count_down_to_reach

	def packet_print(self):
		print("{source_node : '" + str(self.source_node) + "' \n destination_node : '" + str(self.destination_node) + "'}")		