from NetworksProject import *
import sys

sim = Simulator.Simulator()

sim.set_routing_protocol(("Distance Vector", True, True,1000000))
sim.add_node("A", (1, 3), "1.1.1.0/24")
sim.add_node("B", (3, 3), "2.2.2.0/24")
sim.add_node("C", (5, 3), "3.3.3.0/24")
sim.add_node("D", (7, 3), "4.4.4.0/24")

sim.add_connection("A", "B", 2)
sim.add_connection("B", "C", 3)
sim.add_connection("C", "D", 1)

sim.step()
sim.step()
sim.step()
sim.step()
sim.update_connection("C", "D", float('inf'))

#A----x----B----y-----C--1--D
#A(x+y+1)----B(y+1)-----C(1)--D


if not ( len(sys.argv) > 1 and sys.argv[1] == "--no-gui" ):
    gui = SimulatorPlotter.Gui(sim)
    gui.start()


