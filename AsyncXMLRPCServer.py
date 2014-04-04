from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from threading import Lock, Timer
import socket
import SocketServer
import random
import xmlrpclib
import datetime
# from Synchronized import synchronized, synchronized_check


# def synchronized(lock):
#     def wrap(f):
#         def newFunction(*args, **kw):
#             lock.acquire()
#             try:
#                 return f(*args, **kw)
#             finally:
#                 lock.release()
#         return newFunction
#     return wrap

class AsyncXMLRPCServer(SocketServer.ThreadingMixIn,SimpleXMLRPCServer):
    def __init__(self, uid, request_handler, hosts):
        assert uid < len(hosts)
        self.hosts = hosts
        self.uid = uid
        self.host = hosts[uid]

        self.offset = 0
        self.time_server_set = False
        self.global_time_server = None
        self.am_leader = False

        self.clock_lock = Lock()
        self.vector_clock = [0 for x in xrange(len(hosts))]

        SimpleXMLRPCServer.__init__(self, self.host, request_handler)

    def vector_clock_to_string(self):
        """ Returns string representation of instance's vector clock.
        Example usage:
        >>> a = AsyncXMLRPCServer(0, SimpleXMLRPCRequestHandler, [None])
        >>> a.vector_clock = [1, 10, 12, 4]
        >>> a.vector_clock_to_string()
        '1 10 12 4'
        """
        return " ".join(map(str, self.vector_clock))

    def vector_clock_from_string(self, vector_clock_str):
        """ Returns list representation of a vector clock string.
        Example usage:
        >>> a = AsyncXMLRPCServer(0, SimpleXMLRPCRequestHandler, [None])
        >>> a.vector_clock = [1, 10, 12, 4]
        >>> a.vector_clock_from_string('1 10 12 4')
        [1, 10, 12, 4]
        """
        return map(int, vector_clock_str.split())

    def increment_event_count(self):
        with self.clock_lock:
            self.vector_clock[self.uid] += 1

    # @synchronized(self.clock_lock)
    def synch_vector_clocks(self, vector_clock_str):
        vector_clock = self.vector_clock_from_string(vector_clock_str)
        with self.clock_lock:
            self.vector_clock = [max(i,j) for i,j in zip(self.vector_clock, vector_clock)]
        return self.vector_clock_to_string()

    def get_offset(self):
        return self.offset

    def set_offset(self, offset):
        self.offset = offset

    def get_host(self):
        return self.host

    def check_time_server(self):
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
        if (self.time_server_set == False):
            return False
        elif (self.am_leader):
            return self.host
        else:
            try:
                return self.global_time_server.get_host()
            except socket.error:
                return False

    def elect_leader(self):
        return self.elect_leader()

    def get_id(self):
        return self.uid

    def get_processes(self):
        processes={}
        for (server_ip, server_port) in self.hosts:
            try:
                server = xmlrpclib.ServerProxy("http://%s:%d"%(server_ip, server_port))
                uid = server.get_id()
                if uid != self.uid:
                    processes[uid] = server
            except socket.error:
                pass
        print "*************"
        print processes
        print "*************"
        return processes

    def am_leader(self):
        return self.am_leader

    def check_server_activity(self):
        print self.global_time_server
        if (self.am_leader == True):
            print "Time server connected."
            return "Time server connected."
        elif (self.time_server_set == False):
            print "There is currently no time server. Fetching from existing process."
            if (self.fetch_time_server() == False):
                print "Fetch failed. Electing a leader."
                self.elect_leader()
        if self.time_server_not_responding():
            print "The time server is not responding." 
            self.elect_leader()
        return "Time server elected."

    def time_server_not_responding(self):
        print "Checking if the time server is responding."
        if not self.time_server_set or self.am_leader:
            print "No time server yet or I am leader."
            return False
        try:
            uid = self.global_time_server.get_id()
        except socket.error:
            self.global_time_server = None
            self.time_server_set = False
            print "Not responding."
            return True
        print "The time server is responding!"
        return False

    def fetch_time_server(self):
        processes = self.get_processes()
        if (len(processes) < 1):
            print "Not enough servers up yet"
            return False
        else:
            server = processes.itervalues().next()
            host = server.get_leader()
            if (host != False):
                self.global_time_server = xmlrpclib.ServerProxy("http://%s:%d"%(host[0], host[1]))
                self.time_server_set = True
                return True
            return False

    def elect_leader(self):
        processes = self.get_processes()
        if (len(processes) < 1):
            print "Not enough servers up yet"
            return "Not enough servers up yet"
        else:
            return self.start_election(processes)

    def start_election(self, processes):
        higher_active_process = False
        for uid, server in processes.iteritems():
            if uid > self.uid:
                try:
                    # TODO: callback function (send back ack immediately)
                    ack = server.elect_leader()
                    print "The ack was " + ack
                    if (ack == "I won!"):
                        self.global_time_server = server
                        self.time_server_set = True
                        print "Leader is %d"%(uid)
                    higher_active_process = True
                    break
                except socket.error:
                    pass
        if (higher_active_process):
            print "I am not leader."
            return "OK"
        else:
            self.am_leader = True
            self.time_server_set = True
            print "I am leader."
            return "I won!"

    def set_offset_for_processes(self):
        processes = self.get_processes()
        if (len(processes) < 1):
            print "Not enough servers up yet"
        times = []
        servers = []
        time = datetime.datetime.now().time()
        secs = (time.hour * 3600) + (time.minute * 60) + time.second
        times.append(secs)
        average = secs
        for server in processes.itervalues():
            servers.append(server)
            server_local_time = server.get_time_in_seconds()
            times.append(server_local_time)
            average += server_local_time
        average = float(average) / len(times)
        self.offset = average - secs
        times.pop(0)
        for i in range(len(servers)):
            servers[i].set_offset(average - times[i])
        t = Timer(5, self.set_offset_for_processes)
        t.daemon = True
        t.start()
        return

