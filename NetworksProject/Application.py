import random

class Application:

    def __init__(self, host, name, protocols, port = None):
        self.host = host
        self.name = name
        self.protocols = protocols
        if port is None:  # Choose a random port if one is not provided
            self.port = random.randint(10000, 65535)
        else:
            self.port = port
    
    def process_packet(self, packet):
        return

    def poll_periodic_update(self):
        return
