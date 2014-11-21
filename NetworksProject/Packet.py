import math

class Packet:

    def __init__(self,src_type, dst_type, src, dst, link_src, link_dst, protocol, ttl, cost, data):
        self.src_type = src_type
        self.dst_type = dst_type
        self.src = src
        self.dst = dst
        self.link_src = link_src
        self.link_dst = link_dst
        self.ttl = ttl
        self.protocol = protocol
        self.data = data
        self.cost = cost

    def set_count_down(self,connection):
        self.count_down_to_reach = math.floor(connection.distance/connection.clock_step)

    def update_packet(self):
        self.count_down_to_reach -= 1
        return self.count_down_to_reach

    def packet_print(self):
        print("{source_node : '" + str(self.source_node) + "' \n destination_node : '" + str(self.destination_node) + "'}")		
