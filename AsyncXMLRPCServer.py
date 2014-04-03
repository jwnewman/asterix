from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
import threading
import socket
import SocketServer
import random
import xmlrpclib
import datetime

class AsyncXMLRPCServer(SocketServer.ThreadingMixIn,SimpleXMLRPCServer):
    def __init__(self, host, request_handler, hosts):
        self.uid = random.randint(0,100)
        self.offset = 0
        self.host = host
        self.hosts = hosts
        self.time_server_set = False
        self.global_time_server = None
        self.am_leader = False
        SimpleXMLRPCServer.__init__(self, host, request_handler)

    def get_offset(self):
        return self.offset

    def set_offset(self, offset):
        self.offset = offset

    def get_host(self):
        return self.host

    def check_time_server(self):
        ack = self.check_server_activity()
        if self.am_leader:
            t = threading.Timer(30, self.set_offset_for_processes)
            t.daemon = True
            t.start()
        else:
            t = threading.Timer(60, self.check_time_server)
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

###

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
        print processes
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
        t = threading.Timer(30, self.set_offset_for_processes)
        t.daemon = True
        t.start()
        return

