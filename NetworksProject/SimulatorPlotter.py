import tkinter as tk
from TraceRoute import *

class NodeInformation(tk.Frame):
	width = 600

	def __init__(self, master=None):
		tk.Frame.__init__(self, master)
		self.pack()
		self.create_widgets()

	def create_widgets(self):
		self.canvas = tk.Canvas(self, width=self.width, height=450)
		self.canvas.pack()
		

	def create_data(self,node_forwarding_table,node_type):
		self.canvas.delete("all")
		y_delta = 15
		y_pos = y_delta
		color = ["#e1f5fe","#b3e5fc"]
		if(node_type == "CONNECTION"):
			color = ["#FFEBEE","#FFCDD2"]

		pos = 0
		if(node_type == "NODE"):
			text_to_write = "Dst IP    NextHop    Distance"
		if(node_type == "CONNECTION"):
			text_to_write = "Source   SourceType   Destn   DestnType   TTL   Protocol  Position"
		
		self.canvas.create_text(
			self.width/2, y_pos,
			text=text_to_write,	font="14")
		y_pos += 2*y_delta
		pos = 1-pos

		for key,value in node_forwarding_table.items():
			self.canvas.create_rectangle(
				0,	y_pos-y_delta,
				self.width, y_pos+y_delta,
				fill=color[pos], width="0.0" )
			if(node_type=="NODE"):
				text_to_write = str(key)+"          "+str(value[0])+"               "+str(value[1])
			if(node_type=="CONNECTION"):
				text_to_write = str(value.src) + "    " \
				+ str(value.src_type) + "      " + str(value.dst) \
				+ "     " +str(value.dst_type) + "    " \
				+  str(value.ttl) + "      " + str(value.protocol) \
				+ "   " + str(value.link_src) + "->" + str(value.link_dst)

			self.canvas.create_text(
				self.width/2, y_pos,
				text=text_to_write,	font="14")
			y_pos += 2*y_delta
			pos = 1 - pos

class Application(tk.Frame):	
	circle_radius = 25
	small_circle_radius = 10
	scale_factor = 100
	sim = None
	node_info = None
	forwarding_table = dict()
	callback_position = dict()
	line_color = "#263238"
	connection_color = "#90A4AE"
	focused = None
	entrytext_src_ip = ""
	entrytext_dst_ip = ""
	
	def is_click_in(self,position,click):
		px = int(position[0])
		py = int(position[1])
		rd = int(position[2])
		cx = int(click[0])
		cy = int(click[1])
		dist_sqr = (px - cx)*(px - cx) + (py - cy)*(py - cy)
		return dist_sqr <= rd*rd

	def mouse_callback(self,event):
		click = (event.x,event.y)
		for key,pstn in self.callback_position.items():
			if(self.is_click_in(pstn,click)):
				self.node_info.show_node_info(self.sim,key,pstn[3])
				self.focused = (self.sim,key,pstn[3])

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
		self.step.pack()

		self.step= tk.Button(self)
		self.step["text"] = "SHOW ALL PACKETS"
		self.step["command"] = self.show_all_packets
		self.step.pack()

		label_src_ip = tk.Label(self, text='Source IP')
		label_src_ip.pack(side="left")

		self.entry_src_ip = tk.Entry(self, textvariable=self.entrytext_src_ip)
		self.entry_src_ip.pack(side="left")
		self.label_dst_ip = tk.Label(self, text='Destination IP')
		self.label_dst_ip.pack(side="left")
		self.entry_dst_ip = tk.Entry(self, textvariable=self.entrytext_dst_ip)
		self.entry_dst_ip.pack(side="left")

		self.step= tk.Button(self)
		self.step["text"] = "TRACE ROUTE"
		self.step["command"] = self.start_traceroute
		self.step.pack(side="left")

	def create_graph(self):
		self.canvas.bind("<Button-1>", self.mouse_callback)
		#To Plot the connection between nodes 
		for keys,node in self.sim.nodes.items():
			for neighbour,cost in node.neighbours.items():
				if(keys >= neighbour):
					continue
				p1x = node.position[0]*self.scale_factor
				p1y = node.position[1]*self.scale_factor 
				p2x = self.sim.nodes[neighbour].position[0]*self.scale_factor
				p2y = self.sim.nodes[neighbour].position[1]*self.scale_factor
				cx = (p1x+p2x)/2
				cy = (p1y+p2y)/2
				self.canvas.create_line(
					p1x,p1y,
					p2x,p2y,
					fill=self.line_color)
				self.canvas.create_oval(
					cx - self.small_circle_radius,
					cy - self.small_circle_radius,
					cx + self.small_circle_radius,
					cy + self.small_circle_radius,
					fill=self.connection_color,
					width="0.0"
					)
				self.canvas.create_text(cx,cy,text=cost,fill="#ffffff")
				self.callback_position[(keys,neighbour)] = (cx,cy,self.small_circle_radius,"CONNECTION")

		for keys,node in self.sim.nodes.items():
			nx = node.position[0]*self.scale_factor 
			ny = node.position[1]*self.scale_factor
			rd = self.circle_radius
			rds = self.small_circle_radius
			#To create hosts
			for keyid,host in node.hosts.items():
				hx = host.position[0]*self.scale_factor
				hy = host.position[1]*self.scale_factor
				self.canvas.create_line(
					nx,ny,
					hx,hy,
					fill=self.line_color)
				self.canvas.create_oval(
					(nx+hx)/2 - rds, (ny + hy)/2 - rds,
					(nx+hx)/2 + rds, (ny + hy)/2 + rds,
					fill=self.connection_color,width="0.0")
				self.canvas.create_rectangle(
					hx-rd,hy-rd,
					hx+rd,hy+rd,
					fill="#f44336",width="0.0")
				self.canvas.create_text(
					hx,	hy,
					fill="#ffffff",text=host.ip)
				self.callback_position[(keys,host.ip)] = ((nx+hx)/2,(ny+hy)/2,rds,"CONNECTION")

			self.canvas.create_oval(
				nx - rd, ny - rd,
				nx + rd, ny + rd,
				fill="#81d4fa",width="0.0")
			self.canvas.create_text(
				nx,ny,
				text=node.name)
			self.callback_position[keys] = (nx,ny,rd,"NODE")

	def step_simulation(self):
		if(self.sim != None):
			self.sim.step()
			if(self.focused != None):
				self.node_info.show_node_info(self.focused[0],self.focused[1],self.focused[2])
	def show_all_packets(self):
		self.focused = (self.sim,("*","*"),"CONNECTION")
		self.node_info.show_node_info(self.focused[0],self.focused[1],self.focused[2])

	def start_traceroute(self):
		start_ip = self.entry_src_ip.get()
		end_ip = self.entry_dst_ip.get()
		print(start_ip + " -> " + end_ip)
		host_obj = None
		for keys,node in self.sim.nodes.items():
			if(start_ip in node.hosts.keys()):
				host_obj = node.hosts[start_ip]
				break
		if(host_obj != None):
			print("Starting Trace Route")
			tr = TraceRoute(host_obj, "TraceRoute")
			tr.trace(end_ip)
		else:
			print("Could Not Find Host")

class NodeInfo:
	root = tk.Tk()
	app = None
	def __init__(self):
		rt = self.root
		self.app = NodeInformation(master=rt)

	def start(self):
		self.app.mainloop()

	def get_packets_in(self,simulator,host1,host2):
		packet_list = {}
		count = 0
		for packet in simulator.packets + simulator.new_packets:
			add_packet = False
			if(host1 != "*" and host2 != "*" and packet.link_src == host1 and packet.link_dst == host2):
				add_packet = True
			elif(host1 != "*" and host2 != "*" and packet.link_src == host2 and packet.link_dst == host1):
				add_packet = True				
			elif(host1 == "*" and host2 != "*" and (packet.link_src == host2 or packet.link_dst == host2)):
				add_packet = True
			elif(host2 == "*" and host1 != "*" and (packet.link_src == host1 or packet.link_dst == host1)):
				add_packet = True
			elif(host1 == "*" and host2 == "*"):
				add_packet = True
			
			if(add_packet):
				packet_list[count] = packet
				count += 1
		return packet_list

	def show_node_info(self,simulator,node_key,node_type):
		if(node_type=="NODE"):
			self.app.create_data(simulator.nodes[node_key].forwarding_table,node_type)
		if(node_type=="CONNECTION"):
			self.app.create_data(self.get_packets_in(simulator,node_key[0],node_key[1]),node_type)



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