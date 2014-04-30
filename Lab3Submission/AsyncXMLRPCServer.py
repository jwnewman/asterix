"""Module for AsyncXMLRPCServer class.  

Includes main methods for vector clocks."""

from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from threading import Lock, Timer
import socket
import SocketServer
import random
import xmlrpclib
import time

def vector_clock_to_string(vector_clock):
    """ Returns string representation of instance's vector clock.

    Example usage:
    >>> vector_clock_to_string([1, 10, 12, 4])
    '1 10 12 4'
    """
    return " ".join(map(str, vector_clock))

def vector_clock_from_string(vector_clock_str):
    """Returns list representation of a vector clock string.

    Example usage:
    >>> vector_clock_from_string('1 10 12 4')
    [1, 10, 12, 4]
    """
    return map(int, vector_clock_str.split())

def sync_vector_clocks(vector_clock_1, vector_clock_2):
    """Returns sync of two vector clocks.

    Synced vector clock is the max along each index of both.

    Arguments:
    vector_clock_1 -- List representation of first vector clock to sync.
    vector_clock_2 -- List representation of second vector clock to sync.
    """
    return [max(i,j) for i,j in zip(vector_clock_1, vector_clock_2)]

class AsyncXMLRPCServer(SocketServer.ThreadingMixIn,SimpleXMLRPCServer):
    """Basic server class that front- and back-end servers inherit from.

    Arguments:
    uid -- Int that uniquely identifies server (used to index into vector clocks).
    request_handler -- RPCHandler object.
    hosts -- List of (ip, port) tuples that are the addresses of other servers.
    """
    def __init__(self, uid, request_handler, hosts):
        assert uid < len(hosts) # uid is used as index into vector clock
        self.hosts = hosts
        self.uid = uid
        self.host = hosts[uid]

        self.offset = 0.0
        self.time_server_set = False
        self.global_time_server = None
        self.am_leader = False

        self.clock_lock = Lock()
        self.vector_clock = [0 for x in xrange(len(hosts))]

        SimpleXMLRPCServer.__init__(self, self.host, request_handler)


    def get_offset(self):
        """Returns current time offset: fraction of secs (float)."""
        return self.offset

    def set_offset(self, offset):
        """Sets current time offset.

        Arguments:
        offset -- Float, fraction of secs
        """
        self.offset = offset

    def get_host(self):
        """Returns (ip, port) tuple that is address of server."""
        return self.host

    def check_time_server(self):
        """Sets Timers to repeatedly set offsets (if leader) or check time server."""
        ack = self.check_server_activity()
        if self.am_leader:
            t = Timer(5, self.set_offset_for_processes)
            t.daemon = True
            t.start()
        else:
            t = Timer(10, self.check_time_server)
            t.daemon = True
            t.start()
        return ack

    def get_time_server_host(self):
        """Returns (ip, port) tuple for current time server.

        Returns False if current time server doesn't exist or is down.
        """
        if self.am_leader:
            return self.host
        if not self.time_server_set:
            return False
        try:
            return self.global_time_server.get_host()
        except socket.error:
            return False

    def get_id(self):
        """Returns unique int ID (used for indexing into vector clocks)."""
        return self.uid

    def get_processes(self):
        """Returns (uid, server) key-value dict for all known processes."""
        processes={}
        for (server_ip, server_port) in self.hosts:
            try:
                server = xmlrpclib.ServerProxy("http://%s:%d"%(server_ip, server_port))
                uid = server.get_id()
                if uid != self.uid:
                    processes[uid] = server
            except socket.error:
                pass
        return processes

    def check_server_activity(self):
        """Checks to see if the current time server is up.  If not, starts an election.

        Returns a string representing the outcome.
        """
        if (self.am_leader == True):
            return "Time server connected."
        elif (self.time_server_set == False):
            print "I am not aware of a time server. Fetching from existing process."
            if (self.fetch_time_server() == False):
                print "Fetch failed. Electing a leader."
                self.start_election()
        if self.time_server_not_responding():
            print "The time server is not responding." 
            self.start_election()
        return "Time server elected."

    def time_server_not_responding(self):
        """Returns True/False whether current time server is responsive."""
        if not self.time_server_set:
            return False
        if self.am_leader:
            return False
        try:
            uid = self.global_time_server.get_id()
        except socket.error:
            self.global_time_server = None
            self.time_server_set = False
            print "The time server is not responding."
            return True
        print "The time server is responding!"
        return False

    def fetch_time_server(self):
        """Returns True/False whether a time server exists. 

        If time server exists, global_time_server and timer_server_set are updated.
        """
        processes = self.get_processes()
        if processes:
            server = processes.itervalues().next()
            host = server.get_leader()
            if host:
                self.global_time_server = xmlrpclib.ServerProxy("http://%s:%d"%(host[0], host[1]))
                self.time_server_set = True
            return True if host else False
        else:
            print "Not enough servers up yet. Cannot fetch a time server."
            return False

    def start_election(self):
        """Implements the Bully algorithm for elections.

        Returns String with the outcome of the election.
        """
        print "---------\nStarting an election...\n---------"
        processes = self.get_processes()
        if len(processes) == 0:
            print "Not enough servers up yet. Cannot initiate election."
            return "Not enough servers up yet."
        higher_active_process = False
        for uid, server in processes.iteritems():
            if uid <= self.uid:
                continue # only contact higher processes
            try:
                ack = server.elect_leader()
                if (ack == "I am leader."):
                    self.global_time_server = server
                    self.time_server_set = True
                    print "OUTCOME:\nLeader is %d\n---------"%(uid)
                higher_active_process = True
                break
            except socket.error:
                pass
        if higher_active_process:
            return "I am NOT leader."
        else:
            self.am_leader = True
            self.time_server_set = True
            print "OUTCOME:\nI am leader.\n---------"
            return "I am leader."

    def set_offset_for_processes(self):
        """Set the offset for all other processes.

        Only called if server is the time server.
        """
        processes = self.get_processes()
        if (len(processes) == 0):
            print "Not enough servers up yet. Cannot synchronize clocks."
            return "Cannot synchronize clocks yet."
        servers = list(processes.itervalues())

        local_time = time.time()
        times = [server.get_time_in_seconds() for server in servers]
        avg_time = (sum(times) + local_time)/(len(times) + 1.0)

        self.offset = avg_time - local_time
        for s, t in zip(servers, times):
            s.set_offset(avg_time - t)

        t = Timer(5, self.set_offset_for_processes)
        t.daemon = True
        t.start()
        return "Clocks synchronized."

if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)
