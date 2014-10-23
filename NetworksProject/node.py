class node:
	processing_time = 0
	max_update_limit = 50

	def __init__(self,id,name,position,processor):
		self.id = id
		self.name = name
		self.position = position
		self.processor = processor
		self.forwarding_table = {}
		self.forwarding_table[name] = [0,name]
		self.count_to_update = 0
		self.neighbours = []

	def add_connection(self,node_name):
		self.neighbours.append(node_name)

	def process_packet(self,pckt):
		print("node_process_packet")
		return self.processor.process_packet(self.forwarding_table,pckt)

	def update_node(self):
		print("update_node")
		print("" + self.name + " : " + str(len(self.forwarding_table.keys())))
		self.count_to_update += 1
		if(self.count_to_update == self.max_update_limit):
			print("maxed_out")
			self.count_to_update = 0
			return self.forwarding_table.keys()
		return []

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
