#!/usr/bin/env python

import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
import threading
import socket
import time
import getopt
import os
import sys
from DatabaseManager import DatabaseManager
from AsyncXMLRPCServer import AsyncXMLRPCServer
from ServerFunctions import ServerFunctions

class DBServerFunctions(ServerFunctions):
    def __init__(self, server):
        self.db_mgr = DatabaseManager()
        ServerFunctions.__init__(self, server)

    def set_score(self, event_type, score, timestamp):
        return self.db_mgr.set_score(event_type, score, timestamp)

    def get_score(self, event_type, client_id, vector_clock_str):
        synched_clock_str = self.server.synch_vector_clocks(vector_clock_str)
        self.db_mgr.check_raffle(client_id, synched_clock_str)
        return synched_clock_str, self.db_mgr.get_medal_tally(team_name)

    def increment_medal_tally(self, team_name, medal_type, timestamp):
        return self.db_mgr.increment_medal_tally(team_name, medal_type, timestamp)

    def get_medal_tally(self, team_name, client_id, vector_clock_str):
        synched_clock_str = self.server.synch_vector_clocks(vector_clock_str)
        self.db_mgr.check_raffle(client_id, synched_clock_str)
        return synched_clock_str, self.db_mgr.get_medal_tally(team_name)
    
class DatabaseRPCHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

    def do_POST(self):
        clientIP, clientPort = self.client_address
        print clientIP, clientPort
        SimpleXMLRPCRequestHandler.do_POST(self)

def main(ip, port=8000, uid=0):
    hosts = [(ip, port), ('localhost', 8002), ('localhost', 8003)] # Fix this... this is simply the hosts of all the three servers
    server = AsyncXMLRPCServer(uid, DatabaseRPCHandler, hosts)
    server.register_introspection_functions()
    server.register_instance(DBServerFunctions(server))
    t = threading.Timer(10, server.check_time_server)
    t.daemon = True
    t.start()
    server.serve_forever()
        

if __name__ == "__main__":
    main("localhost", 8000, 0) #TODO: Delete me
   
    try:
        opts, args = getopt.getopt(sys.argv[1:], "", ["run_locally=","serport="])
    except getopt.error, msg:
        print msg
        sys.exit(2)

    run_locally, port = [x[1] for x in opts]
    if run_locally=="True":
        ip = "localhost"
    else:
        print "HOORAY"
        ip = socket.gethostbyname(socket.gethostname())
    print port
    main(ip = ip, port=int(port))

