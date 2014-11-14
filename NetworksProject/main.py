from Simulator import *

sim = Simulator()
sim.add_node("n1", (1, 1), "1.1.1.0/24")
sim.add_host("1.1.1.1", "n1", (2, 2))
sim.add_host("1.1.1.2", "n1", (2, 3))
packet = Packet("Host", "Host", "1.1.1.1", "1.1.1.2", "1.1.1.1", "n1", 1, 100, 1, "blah")
sim.put_packet(packet)
sim.step()
sim.step()
sim.step()
