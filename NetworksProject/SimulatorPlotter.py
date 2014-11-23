import tkinter as tk
import time
from .TraceRoute import *

'''
class for managing the information Tkinter Window
'''
class NodeInformation(tk.Frame):
	'''dimensions of the tkinter'''
	width = 900
	height = 600

	def __init__(self, master=None):
		tk.Frame.__init__(self, master)
		self.pack()
		self.create_widgets()

	def create_widgets(self):
		self.canvas = tk.Canvas(self, width=self.width, height=self.height)
		self.canvas.pack()

	def create_data(self,node_forwarding_table,node_type):
		'''
		create the data to be displayed on the tkinter Window
		'''
		self.canvas.delete("all")
		self.canvas.create_rectangle(0,0,self.width,self.height,fill="#ffffff",width="0.0")
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
				+ "   " + str(value.link_src) + "->" + str(value.link_dst)\
				+ "  " + str(value.data)

			self.canvas.create_text(
				self.width/2, y_pos,
				text=text_to_write,	font="14")
			y_pos += 2*y_delta
			pos = 1 - pos


'''
The core application Gui
'''
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
	canvas_width= 1000
	canvas_height = 500
	top_button_background = "#BBDEFB"
	def_background = "#f1f1f1"
	def_button_background = "#dddddd"
	def_color = "#000000"
	def_button_color = "#000000"
	
	def is_click_in(self,position,click):
		px = int(position[0])
		py = int(position[1])
		rd = int(position[2])
		cx = int(click[0])
		cy = int(click[1])
		dist_sqr = (px - cx)*(px - cx) + (py - cy)*(py - cy)
		return dist_sqr <= rd*rd

	def focus_unfocus(self,focus_ele,ftype):
		if(focus_ele == None):
			return
		position = focus_ele[3]
		sd = self.circle_radius + 2
		outline_color = "#AB47BC"
		if(ftype==0):
			outline_color = "#ffffff"
		self.canvas.create_oval(
			position[0] - sd,position[1]-sd,
			position[0] + sd,position[1]+sd,
			fill="",outline=outline_color,width="2.0")

	def mouse_callback(self,event):
		click = (event.x,event.y)
		for key,pstn in self.callback_position.items():
			if(self.is_click_in(pstn,click)):
				if(self.focused != None):
					self.focus_unfocus(self.focused,0)
				self.node_info.show_node_info(self.sim,key,pstn[3])
				self.focused = (self.sim,key,pstn[3],pstn)
				self.focus_unfocus(self.focused,1)

	def __init__(self, master=None):
		tk.Frame.__init__(self, master,background=self.def_background)
		self.pack()
		self.create_widgets()

	def create_widgets(self):
		'''Top Frame'''
		self.frame_top = tk.Frame(self,background=self.def_background)

		self.entry_step = tk.Entry(self.frame_top,bd="0.0")
		self.entry_step.pack(side="left",padx="5")
		self.entry_step.insert(0,"1")

		self.step= tk.Button(self.frame_top,bg=self.top_button_background,fg=self.def_button_color,bd="0.0",padx="10",pady="5")
		self.step["text"] = "STEP"
		self.step["command"] = self.step_simulation
		self.step.pack(side="left",padx="5")

		self.step= tk.Button(self.frame_top,bg=self.top_button_background,fg=self.def_button_color,bd="0.0",padx="10",pady="5")
		self.step["text"] = "SHOW ALL PACKETS"
		self.step["command"] = self.show_all_packets
		self.step.pack(side="left",padx="5")

		self.step= tk.Button(self.frame_top,bg=self.top_button_background,fg=self.def_button_color,bd="0.0",padx="10",pady="5")
		self.step["text"] = "REFRESH UI"
		self.step["command"] = self.create_graph
		self.step.pack(side="left",padx="5")
		self.frame_top.pack(pady="5")

		self.canvas = tk.Canvas(self, width=self.canvas_width, height=self.canvas_height)
		self.canvas.pack(pady="1")
		# self.start = tk.Button(self)


		self.frame_bottom = tk.Frame(self,background=self.def_background)
		label_src_ip = tk.Label(self.frame_bottom, text='Source IP : ',background=self.def_background,foreground=self.def_color)
		label_src_ip.pack(side="left",padx="5")
		self.entry_src_ip = tk.Entry(self.frame_bottom,bd="0.0")
		self.entry_src_ip.pack(side="left",padx="5")
		self.label_dst_ip = tk.Label(self.frame_bottom, text='   Destination IP : ',background=self.def_background,foreground=self.def_color)
		self.label_dst_ip.pack(side="left",padx="5")
		self.entry_dst_ip = tk.Entry(self.frame_bottom,bd="0.0")
		self.entry_dst_ip.pack(side="left",padx="5")

		self.step= tk.Button(self.frame_bottom,bg=self.def_button_background,fg=self.def_button_color,bd="0.0",padx="10",pady="5")
		self.step["text"] = "TRACE ROUTE"
		self.step["command"] = self.start_traceroute
		self.step.pack(side="left",padx="5")

		self.frame_bottom.pack()

		self.frame_dummy=tk.Frame(self)
		self.frame_dummy.pack(pady="5")

		'''
		ADDING NEW CONNECTION
		'''

		self.frame_connection_1 = tk.Frame(self,background=self.def_background)
		self.frame_connection_2 = tk.Frame(self,background=self.def_background)

		label_update_node_1 = tk.Label(self.frame_connection_1, text='Node 1 : ',background=self.def_background,foreground=self.def_color)
		label_update_node_1.pack(side="left",padx="5")
		self.entry_update_node_1 = tk.Entry(self.frame_connection_1,bd="0.0")
		self.entry_update_node_1.pack(side="left",padx="5")
		self.label_update_node_2 = tk.Label(self.frame_connection_1, text='  Node 2 : ',background=self.def_background,foreground=self.def_color)
		self.label_update_node_2.pack(side="left",padx="5")
		self.entry_update_node_2 = tk.Entry(self.frame_connection_1,bd="0.0")
		self.entry_update_node_2.pack(side="left",padx="5")
		self.label_update_node_value = tk.Label(self.frame_connection_2, text='  Value : ',background=self.def_background,foreground=self.def_color)
		self.label_update_node_value.pack(side="left",padx="5")
		self.entry_update_node_value = tk.Entry(self.frame_connection_2,bd="0.0")
		self.entry_update_node_value.pack(side="left",padx="5")

		self.step= tk.Button(self.frame_connection_2,bg=self.def_button_background,fg=self.def_button_color,bd="0.0",padx="10",pady="5")
		self.step["text"] = "UPDATE CONNECTION"
		self.step["command"] = self.update_connection
		self.step.pack(side="left",padx="5")

		self.step= tk.Button(self.frame_connection_2,bg=self.def_button_background,fg=self.def_button_color,bd="0.0",padx="10",pady="5")
		self.step["text"] = "REMOVE CONNECTION"
		self.step["command"] = self.remove_connection
		self.step.pack(side="left",padx="5")

		self.frame_connection_1.pack(pady="1")
		self.frame_connection_2.pack(pady="1")

		self.frame_dummy_2=tk.Frame(self)
		self.frame_dummy_2.pack(pady="5")

		'''
		ADDING NEW NODE
		'''
		self.frame_node_1 = tk.Frame(self,background=self.def_background)
		self.frame_node_2 = tk.Frame(self,background=self.def_background)

		label_create_node_name = tk.Label(self.frame_node_1, text='Name : ',background=self.def_background,foreground=self.def_color)
		label_create_node_name.pack(side="left",padx="5")
		self.entry_create_node_name = tk.Entry(self.frame_node_1,bd="0.0")
		self.entry_create_node_name.pack(side="left",padx="5")

		label_create_node_ip = tk.Label(self.frame_node_2, text='IP/Subnet : ',background=self.def_background,foreground=self.def_color)
		label_create_node_ip.pack(side="left",padx="5")
		self.entry_create_node_ip = tk.Entry(self.frame_node_2,bd="0.0")
		self.entry_create_node_ip.pack(side="left",padx="5")

		self.label_create_node_posx = tk.Label(self.frame_node_1, text='  PosX : ',background=self.def_background,foreground=self.def_color)
		self.label_create_node_posx.pack(side="left",padx="5")
		self.entry_create_node_posx = tk.Entry(self.frame_node_1,bd="0.0")
		self.entry_create_node_posx.pack(side="left",padx="5")

		self.label_create_node_posy = tk.Label(self.frame_node_1, text='  PosY : ',background=self.def_background,foreground=self.def_color)
		self.label_create_node_posy.pack(side="left",padx="5")
		self.entry_create_node_posy = tk.Entry(self.frame_node_1,bd="0.0")
		self.entry_create_node_posy.pack(side="left",padx="5")

		self.step= tk.Button(self.frame_node_2,bg=self.def_button_background,fg=self.def_button_color,bd="0.0",padx="10",pady="5")
		self.step["text"] = "ADD NODE"
		self.step["command"] = self.add_new_node
		self.step.pack(side="left",padx="5")

		self.step= tk.Button(self.frame_node_2,bg=self.def_button_background,fg=self.def_button_color,bd="0.0",padx="10",pady="5")
		self.step["text"] = "REMOVE NODE"
		self.step["command"] = self.remove_node
		self.step.pack(side="left",padx="5")

		self.frame_node_1.pack(pady="1")
		self.frame_node_2.pack(pady="1")

		self.frame_dummy=tk.Frame(self)
		self.frame_dummy.pack(pady="5")
		'''
		ADDING NEW NODE
		'''
		self.frame_host_1 = tk.Frame(self,background=self.def_background)
		self.frame_host_2 = tk.Frame(self,background=self.def_background)

		label_create_host_name = tk.Label(self.frame_host_1, text='Parent : ',background=self.def_background,foreground=self.def_color)
		label_create_host_name.pack(side="left",padx="5")
		self.entry_create_host_name = tk.Entry(self.frame_host_1,bd="0.0")
		self.entry_create_host_name.pack(side="left",padx="5")

		label_create_host_ip = tk.Label(self.frame_host_2, text='IP : ',background=self.def_background,foreground=self.def_color)
		label_create_host_ip.pack(side="left",padx="5")
		self.entry_create_host_ip = tk.Entry(self.frame_host_2,bd="0.0")
		self.entry_create_host_ip.pack(side="left",padx="5")

		self.label_create_host_posx = tk.Label(self.frame_host_1, text='  PosX : ',background=self.def_background,foreground=self.def_color)
		self.label_create_host_posx.pack(side="left",padx="5")
		self.entry_create_host_posx = tk.Entry(self.frame_host_1,bd="0.0")
		self.entry_create_host_posx.pack(side="left",padx="5")

		self.label_create_host_posy = tk.Label(self.frame_host_1, text='  PosY : ',background=self.def_background,foreground=self.def_color)
		self.label_create_host_posy.pack(side="left",padx="5")
		self.entry_create_host_posy = tk.Entry(self.frame_host_1,bd="0.0")
		self.entry_create_host_posy.pack(side="left",padx="5")

		self.step= tk.Button(self.frame_host_2,bg=self.def_button_background,fg=self.def_button_color,bd="0.0",padx="10",pady="5")
		self.step["text"] = "ADD HOST"
		self.step["command"] = self.add_new_host
		self.step.pack(side="left",padx="5")

		self.step= tk.Button(self.frame_host_2,bg=self.def_button_background,fg=self.def_button_color,bd="0.0",padx="10",pady="5")
		self.step["text"] = "REMOVE HOST"
		self.step["command"] = self.remove_host
		self.step.pack(side="left",padx="5")

		self.frame_host_1.pack(pady="1")
		self.frame_host_2.pack(pady="1")

		self.frame_dummy=tk.Frame(self)
		self.frame_dummy.pack(pady="5")

	def create_graph(self):
		'''Resetting the canvas background'''
		self.canvas.create_rectangle(0,0,self.canvas_width,self.canvas_height,fill="#ffffff",width="0.0")
		self.canvas.bind("<Button-1>", self.mouse_callback)
		for i in range(1,10):
			self.canvas.create_line(i*self.scale_factor,0,i*self.scale_factor,self.canvas_height,fill="#eeeeee")
			self.canvas.create_text(i*self.scale_factor,10,text=str(i),fill="#aaaaaa")
			self.canvas.create_line(0,i*self.scale_factor,self.canvas_width,i*self.scale_factor,fill="#eeeeee")
			self.canvas.create_text(10,i*self.scale_factor,text=str(i),fill="#aaaaaa")
		if(self.sim.routing == "Link State"):
			self.canvas.create_text(self.canvas_width-100,30,text="Link State Routing")
		else:
			self.canvas.create_text(self.canvas_width-100,30,text="Distance Vector Routing")

		'''Creating the given network'''
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
		step_count = int(self.entry_step.get())
		if(self.sim != None):
			while(step_count != 0):
				self.sim.step()
				if(self.focused != None):
					self.node_info.show_node_info(self.focused[0],self.focused[1],self.focused[2])
				step_count -= 1

	def show_all_packets(self):
		self.focus_unfocus(self.focused,0)
		self.focused = (self.sim,("*","*"),"CONNECTION",(-20,-20))
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

	def update_connection(self):
		start_node = self.entry_update_node_1.get()
		end_node = self.entry_update_node_2.get()
		value = int(self.entry_update_node_value.get())
		self.canvas.delete("all")
		self.sim.update_connection(start_node,end_node,value)
		self.create_graph()

	def remove_connection(self):
		start_node = self.entry_update_node_1.get()
		end_node = self.entry_update_node_2.get()
		self.canvas.delete("all")
		self.sim.update_connection(start_node,end_node,float('inf'))
		self.create_graph()

	def add_new_node(self):
		ip = self.entry_create_node_ip.get()
		px = int(self.entry_create_node_posx.get())
		py = int(self.entry_create_node_posy.get())
		name = self.entry_create_node_name.get()
		self.sim.add_node(name, (px, py), ip)
		self.create_graph()

	def remove_node(self):
		name = self.entry_create_node_name.get()
		self.sim.remove_node(name)
		self.create_graph()

	def add_new_host(self):
		ip = self.entry_create_host_ip.get()
		px = int(self.entry_create_host_posx.get())
		py = int(self.entry_create_host_posy.get())
		name = self.entry_create_host_name.get()
		self.sim.add_host(ip,name, (px, py))
		self.create_graph()

	def remove_host(self):
		name = self.entry_create_host_name.get()
		ip = self.entry_create_host_ip.get()
		self.sim.remove_host(ip,name)
		self.create_graph()

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