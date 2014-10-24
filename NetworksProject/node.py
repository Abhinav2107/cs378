class node:
	processing_time = 0
	max_update_limit = 1000

	def __init__(self,id,name,position):
		self.id = id
		self.name = name
		self.position = position
		self.forwarding_table = {}
		self.forwarding_table[name] = [0,name]
		self.count_to_update = 0
		self.neighbours = {}

	def add_connection(self,node_name,distance):
		self.neighbours[node_name] = distance
		self.forwarding_table[node_name] = [distance,node_name]

	def process_packet(self,pckt):
		return self.processor.process_packet(self.forwarding_table,pckt)

	def update_node(self):
		self.count_to_update -= 1
		if(self.count_to_update ==  -1):
			self.count_to_update = self.max_update_limit
			return [self.name, self.forwarding_table.keys()]
		return [self.name,[]]

class connection:
	id = 0
	nodes = []
	distance = 0
	clock_step = 0
	def __init__(self,id,nodes,distance,clock_step):
		self.id = id
		self.nodes = nodes
		self.distance = distance
		self.clock_step = clock_step
