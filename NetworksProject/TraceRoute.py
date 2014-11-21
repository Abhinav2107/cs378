from Application import *
from Packet import *

class TraceRoute(Application):

    def __init__(self, host, name):
        super().__init__(host, name, ["UDP", "ICMP"])
        self.target = None
        self.path = None
        self.next_ttl = None
        self.done = True
        host.add_app(self)

    def trace(self, target):
        if not self.done:
            print("[ERROR] Another trace already in progress!")
        self.done = False
        self.path = [self.host.ip]
        self.target = target
        self.next_ttl = 1
        packet = Packet("Host", "Host", self.host.ip, self.target, self.host.ip, self.host.node, "UDP", self.next_ttl, 1, (self.port, self.port, None))
        self.host.simulator.put_packet(packet)
        self.next_ttl += 1

    def process_packet(self, packet):
        if packet.protocol == "ICMP" and packet.data[0] == "TTL Expired in Transit":
            self.path.append(packet.src)
            packet = Packet("Host", "Host", self.host.ip, self.target, self.host.ip, self.host.node, "UDP", self.next_ttl, 1, (self.port, self.port, None))
            self.host.simulator.put_packet(packet)
            self.next_ttl += 1
        elif (packet.protocol == "ICMP" and packet.data[0] == "Port Unreachable") or (packet.protocol == "UDP" and packet.src == self.target):
            self.path.append(self.target)
            self.done = True
        elif (packet.protocol == "ICMP" and (packet.data[0] == "Network Unreachable" or packet.data[0] == "Host Unreachable")):
            self.path.append(packet.src)
            self.path.append("Target " + self.target  + " Unreachable")
            self.done = True

    def print(self):
        print("\n=== TraceRoute ===\n")
        i = 1
        for _ in self.path:
            print(str(i)+" : "+_)
            i += 1
        print("\n=== End TraceRoute ===\n")

