import sys
sys.path.insert(0, '../')
from NetworksProject import *

sim = Simulator.Simulator()

sim.set_routing_protocol(("Distance Vector",False,False,120))
sim.add_node("A", (1, 3), "1.1.1.0/24")
sim.add_node("B", (3, 3), "2.2.2.0/24")
sim.add_node("C", (5, 3), "3.3.3.0/24")
sim.add_node("D", (7, 3), "4.4.4.0/24")
sim.add_node("E", (3, 2), "5.5.5.0/24")
sim.add_node("F", (5, 2), "6.6.6.0/24")

host_1 = sim.add_host("1.1.1.1","A", (1, 2))
host_2 = sim.add_host("4.4.4.4","D", (7, 2))

sim.add_connection("A", "B", 2)
sim.add_connection("B", "C", 8)
sim.add_connection("C", "D", 1)
sim.add_connection("E", "B", 2)
sim.add_connection("F", "C", 3)
sim.add_connection("F", "E", 2)

for i in range(0,30):
	sim.step()

tr = TraceRoute.TraceRoute(host_1, "TraceRoute")
tr.trace("4.4.4.4")

if not ( len(sys.argv) > 1 and sys.argv[1] == "--no-gui" ):
    gui = SimulatorPlotter.Gui(sim)
    gui.start()


