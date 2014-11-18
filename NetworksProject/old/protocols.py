from distance_vector import *

class protocols:
	protocol_map = {}
	'''
		P1 : Distance Vector
		P2 : Distance Vector, Split Horizon
		P3 : Distance Vector, Split Horizon Poission Reverse
		Leave more till 10
	'''
	def __init__(self):
		self.protocol_map[1] = distance_vector(1)
		self.protocol_map[2] = distance_vector(2)
		self.protocol_map[3] = distance_vector(3)

	def get_protocol(self,protocol_number):
		return self.protocol_map[protocol_number]

