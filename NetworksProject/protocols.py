from distance_vector import *

class protocols:
	protocol_map = {}

	def __init__(self):
		self.protocol_map[1] = distance_vector()

	def get_protocol(self,protocol_number):
		return self.protocol_map[protocol_number]

