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
        """Returns the current time in fractions of seconds since the Epoch."""
        return time.time()

    def get_host(self):
        """Returns (ip, host) tuple that is the address of the server."""
        return self.server.host

    def get_id(self):
        """Returns an int that uniquely identifies the server.

        This id is used as an index into vector clocks for this server.
        """
        return self.server.get_id()

    def get_leader(self):
        """Returns an (ip, host) tuple for the current time server.

        Returns False is the current time server is down.
        """
        return self.server.get_time_server_host()

    def elect_leader(self):
        """Begins an election (see start_election in AsyncXMLRPCServer).

        Returns a string representing the outcome.
        """
        return self.server.start_election()

    def set_offset(self, offset):
        """Sets the current offset from time server.  Returns True.

        Only called by the current time server (leader).

        Arguments:
        offset -- Float representing offset (fractions of sec).
        """
        self.server.set_offset(offset)
        print "Time server has synchronized clocks. New offset is " + str(self.server.offset)
        return True

    def get_timestamp(self):
        """Returns system time plus current offset."""
        return self.server.get_offset() + time.time()
