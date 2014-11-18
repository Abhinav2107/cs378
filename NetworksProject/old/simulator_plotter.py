import tkinter as tk
from simulator import *

class Application(tk.Frame):
	
	circle_radius = 25
	sim = 0
	forwarding_table = {}

	def __init__(self, master=None):
		tk.Frame.__init__(self, master)
		self.pack()
		self.createWidgets()

	def createWidgets(self):
		self.canvas = tk.Canvas(self, width=1000, height=450)
		self.canvas.pack()
		self.start = tk.Button(self)
		self.start["text"] = "Start Simulation"
		self.start["command"] = self.start_simulation
		self.start.pack(side="left")

		self.step= tk.Button(self)
		self.step["text"] = "Step"
		self.step["command"] = self.step_simulation
		self.step.pack(side="left")

		self.run = tk.Button(self)
		self.run["text"] = "Run"
		self.run["command"] = self.run_simulation
		self.run.pack(side="left")
		# self.QUIT = tk.Button(self, text="QUIT", fg="red", command=root.destroy)
		# self.QUIT.pack(side="bottom")

	def start_simulation(self):
		self.sim = setup_simulator()
		for keys,conn in self.sim.connection_set.items(): 
			self.canvas.create_line(
				self.sim.node_set[keys[0]].position[0],
				self.sim.node_set[keys[0]].position[1],
				self.sim.node_set[keys[1]].position[0],
				self.sim.node_set[keys[1]].position[1],
				fill="#01579b",width="2.0")
			pos_x = (self.sim.node_set[keys[0]].position[0]+self.sim.node_set[keys[1]].position[0])/2
			pos_y = (self.sim.node_set[keys[0]].position[1]+self.sim.node_set[keys[1]].position[1])/2
			self.canvas.create_oval(
				pos_x - 7,
				pos_y - 7,
				pos_x + 7,
				pos_y + 7,
				fill="#ffffff",width="0.0")
			self.canvas.create_text(
				pos_x,
				pos_y,
				text = str(conn.distance),width="2.0")
		for keys,node in self.sim.node_set.items():
			self.canvas.create_oval(
				node.position[0]-self.circle_radius,
				node.position[1]-self.circle_radius,
				node.position[0]+self.circle_radius,
				node.position[1]+self.circle_radius,
				fill="#81d4fa",width="0.0")
			self.canvas.create_text(
				node.position[0],
				node.position[1],
				text=node.name)
	def convert_table_to_string(self,table):
		result = ""
		for entry,value in sorted(table.items()): 
			result += str(entry) + " | " +  str(value [0]) + " | " + str(value [1]) + "\n"
		return result

	def create_forwarding_tables(self,node_set):
		for keys,node in node_set.items():
			self.canvas.create_rectangle(
				node.position[2] - 40,
				node.position[3] - 40,
				node.position[2] + 40,
				node.position[3] + 40,
				fill = "#f1f1f1")
			self.canvas.create_text(
				node.position[2],
				node.position[3],
				text = self.convert_table_to_string(node.forwarding_table))

	def step_simulation(self):
		if(self.sim != 0):
			self.sim.step()
			self.create_forwarding_tables(self.sim.node_set)

	def run_simulation(self):
		if(self.sim != 0):
			self.sim.initialise()
			self.create_forwarding_tables(self.sim.node_set)
			self.sim.print_routing_tables()


class Gui:
	root = tk.Tk()
	app = 0
	def __init__(self):
		rt = self.root
		self.app = Application(master=rt)

	def start(self):
		self.app.mainloop()

gui = Gui()
gui.start()