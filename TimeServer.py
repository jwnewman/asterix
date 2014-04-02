import random
import xmlrpclib
import socket

class TimeServer:
    def __init__(self, hosts, my_id, my_host):
        self.hosts = hosts
        self.time_server_set = False
        self.global_time_server = None
        self.home_id = my_id
        self.am_leader = False
        self.host = my_host
        print "TimeServer initialized with hosts:"
        print hosts

    def get_processes(self):
        processes={}
        for (server_ip, server_port) in self.hosts:
            try:
                server = xmlrpclib.ServerProxy("http://%s:%d"%(server_ip, server_port))
                uid = server.get_id()
                if uid != self.home_id:
                    processes[uid] = server
            except socket.error:
                pass
        print processes
        return processes

    def get_leader_host(self):
        if (self.time_server_set == False):
            return False
        elif (self.am_leader):
            return self.host
        else:
            return self.global_time_server.get_host()

    def check_time_server(self):
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
        try:
            id = self.global_time_server.get_id()
        except socket.error:
            self.global_time_server = None
            self.time_server_set = False
            print "Not responding."
            return True
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
            if uid > self.home_id:
                try:
                    ack = server.elect_leader()
                    print "The ack was " + ack
                    if (ack == "I won!"):
                        self.global_time_server = server
                        self.time_server_set = True
                        print "Leader is %d"%(uid)
                    higher_active_process = True
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
        
