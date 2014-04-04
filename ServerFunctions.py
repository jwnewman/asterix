"""Module for ServerFucntions class."""

import time
from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler

class ServerFunctions():
    """ServerFunctions implements the basic clock synchronization methods used by front/backend servers.

    Arguments:
    server -- The active server object implementing these methods.
    """
    def __init__(self, server):
        self.server = server    

    def get_time_in_seconds(self):
        return time.time()

    def get_host(self):
        return self.server.host

    def get_id(self):
        return self.server.get_id()

    def get_leader(self):
        return self.server.get_time_server_host()

    def elect_leader(self):
        return self.server.elect_leader()

    def set_offset(self, offset):
        self.server.set_offset(offset)
        print "New offset is " + str(self.server.offset)
        return True

    def get_timestamp(self):
        return self.server.get_offset() + time.time()