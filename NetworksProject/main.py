from Simulator import *
from SimulatorPlotter import *
from TraceRoute import *
import sys

sim = Simulator()
sim.add_node("n1", (1, 1), "1.1.1.0/24")
sim.add_node("n2", (3, 1), "2.2.2.0/24")
sim.add_node("n3", (5, 1), "3.3.3.0/24")
sim.add_connection("n1", "n2", 1)
sim.add_connection("n2", "n3", 1)
h = sim.add_host("1.1.1.1", "n1", (2, 2))
sim.add_host("3.3.3.3", "n3", (5, 3))
sim.set_routing_protocol(("Distance Vector", False, False))

packet = Packet("Host", "Host", "1.1.1.1", "3.3.3.3", "1.1.1.1", "n1", "UDP", 64, 1, "blah")
sim.step()
sim.step()
sim.step()
sim.step()
sim.step()
sim.step()
#sim.put_packet(packet)
for name, node in sim.nodes.items():
    print(node.forwarding_table)
tr = TraceRoute(h, "TraceRoute")
tr.trace("3.3.3.3")
while not tr.done:
    sim.step()
tr.print()
if not ( len(sys.argv) > 1 and sys.argv[1] == "--no-gui" ):
    gui = Gui(sim)
    gui.start()
