import sys
sys.path.insert(0, '../')
from NetworksProject import *

sim = Simulator.Simulator()

sim.set_routing_protocol(("Link State",120))
sim.add_node("A", (1, 3), "1.1.1.0/24")
sim.add_node("B", (2, 3), "2.2.2.0/24")
sim.add_node("C", (3, 3), "3.3.3.0/24")
sim.add_node("D", (4, 2), "4.4.4.0/24")
sim.add_node("E", (5, 2), "5.5.5.0/24")
sim.add_node("F", (6, 2), "6.6.6.0/24")

sim.add_connection("A", "B", 2)
sim.add_connection("B", "C", 2)
sim.add_connection("C", "D", 2)
sim.add_connection("D", "E", 2)
sim.add_connection("E", "F", 2)

for i in range(0,30):
	sim.step()

sim.update_connection("C","D",float('inf'))
sim.add_node("G", (6, 3), "7.7.7.0/24")
sim.add_node("H", (1, 2), "8.8.8.0/24")
sim.add_connection("G", "F", 2)
sim.add_connection("H", "A", 2)

for i in range(0,30):
	sim.step()

sim.add_connection("C","D",2)

if not ( len(sys.argv) > 1 and sys.argv[1] == "--no-gui" ):
    gui = SimulatorPlotter.Gui(sim)
    gui.start()