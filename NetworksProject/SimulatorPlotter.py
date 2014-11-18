import tkinter as tk

class NodeInformation(tk.Frame):
	def __init__(self, master=None):
		tk.Frame.__init__(self, master)
		self.pack()
		self.create_widgets()

	def create_widgets(self):
		self.canvas = tk.Canvas(self, width=200, height=450)
		self.canvas.pack()

	def create_data(self,node_forwarding_table):
		self.canvas.delete("all")
		y_delta = 15
		y_pos = y_delta
		color = ["#e1f5fe","#b3e5fc"]
		pos = 0
		for key,value in node_forwarding_table.items():
			self.canvas.create_rectangle(
				0,
				y_pos-y_delta,
				200,
				y_pos+y_delta,
				fill=color[pos],
				width="0.0"
				)
			self.canvas.create_text(
				100,
				y_pos,
				text=str(key)+"    "+str(value[0])+"    "+str(value[1]),
				font="14"
				)
			y_pos += 2*y_delta
			pos = 1 - pos

class Application(tk.Frame):	
	circle_radius = 25
	scale_factor = 100
	sim = None
	node_info = None
	forwarding_table = dict()
	callback_position = dict()

	def is_click_in(self,position,click):
		px = int(position[0])
		py = int(position[1])
		cx = int(click[0])
		cy = int(click[1])
		dist_sqr = (px - cx)*(px - cx) + (py - cy)*(py - cy)
		return dist_sqr <= (self.circle_radius)*(self.circle_radius)

	def mouse_callback(self,event):
		click = (event.x,event.y)
		for key,pstn in self.callback_position.items():
		    if(self.is_click_in(pstn,click)):
		    	self.node_info.show_node_info(self.sim,key)

	def __init__(self, master=None):
		tk.Frame.__init__(self, master)
		self.pack()
		self.create_widgets()

	def create_widgets(self):
		self.canvas = tk.Canvas(self, width=1000, height=450)
		self.canvas.pack()
		# self.start = tk.Button(self)

		self.step= tk.Button(self)
		self.step["text"] = "STEP"
		self.step["command"] = self.step_simulation
		self.step.pack(side="left")

	def create_graph(self):
		self.canvas.bind("<Button-1>", self.mouse_callback)
		for keys,node in self.sim.nodes.items():
			for keyid,host in node.hosts.items():
				self.canvas.create_line(
					node.position[0]*self.scale_factor,
					node.position[1]*self.scale_factor,
					host.position[0]*self.scale_factor,
					host.position[1]*self.scale_factor,
					fill="#263238")
				self.canvas.create_rectangle(
					host.position[0]*self.scale_factor-self.circle_radius,
					host.position[1]*self.scale_factor-self.circle_radius,
					host.position[0]*self.scale_factor+self.circle_radius,
					host.position[1]*self.scale_factor+self.circle_radius,
					fill="#f44336",width="0.0")
				self.canvas.create_text(
					host.position[0]*self.scale_factor,
					host.position[1]*self.scale_factor,
					fill="#ffffff",text=host.ip)
			self.canvas.create_oval(
				node.position[0]*self.scale_factor-self.circle_radius,
				node.position[1]*self.scale_factor-self.circle_radius,
				node.position[0]*self.scale_factor+self.circle_radius,
				node.position[1]*self.scale_factor+self.circle_radius,
				fill="#81d4fa",width="0.0")
			self.canvas.create_text(
				node.position[0]*self.scale_factor,
				node.position[1]*self.scale_factor,
				text=node.name)
			self.callback_position[keys] = (node.position[0]*self.scale_factor,node.position[1]*self.scale_factor)

	def step_simulation(self):
		if(self.sim != None):
			self.sim.step()

class NodeInfo:
	root = tk.Tk()
	app = None
	def __init__(self):
		rt = self.root
		self.app = NodeInformation(master=rt)

	def start(self):
		self.app.mainloop()

	def show_node_info(self,simulator,node_key):
		self.app.create_data(simulator.nodes[node_key].forwarding_table)


class Gui:
	root = tk.Tk()
	app = None
	node_info = None
	def __init__(self,sim):
		rt = self.root
		self.app = Application(master=rt)
		self.app.sim = sim
		self.app.node_info = NodeInfo()
		self.app.create_graph()

	def start(self):
		self.app.mainloop()
