class Host:

    processing_time = 0
    max_update_limit = 1000

    def __init__(self,simulator,ip,node, position):
        self.simulator = simulator
        self.ip = ip
        self.node = node
        self.position = position

    def process_packet(self, packet):
        print(self.ip + " received packet from " + packet.src)
