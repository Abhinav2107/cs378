class Host:

    processing_time = 0
    max_update_limit = 1000

    def __init__(self,simulator,ip,node, position):
        self.simulator = simulator
        self.ip = ip
        self.node = node
        self.position = position
        self.apps = []

    def process_packet(self, packet):
        toPrint = self.ip + " received " + packet.protocol + " packet from " + packet.src
        if packet.protocol == "ICMP":
            toPrint = self.ip + " received " + packet.protocol + " packet with message \"" + packet.data[0] + "\" from " + packet.src
        print(toPrint)
        if packet.protocol == "UDP":  # Demux UDP packets by port number
            port_unreachable = True
            for app in self.apps:
                if "UDP" in app.protocols and app.port == packet.data[1]:
                    app.process_packet(packet)
                    port_unreachable = False
            if port_unreachable:
                self.simulator.error(self.simulator.nodes[self.node], "Port Unreachable", packet)  # Generate an ICMP packet if no application is running on this port
        else:  # For non-UDP packets, check which applications want this protocol's packets
            for app in self.apps:
                if packet.protocol in app.protocols:
                    app.process_packet(packet)

    def add_app(self, app):
        self.apps.append(app)

    def remove_app(self, app):
        self.apps.remove(app)

    def poll_periodic_update(self):
        for app in self.apps:
            app.poll_periodic_update()
