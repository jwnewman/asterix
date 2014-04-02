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

class DBServerFunctions:
    def __init__(self, server):
        self.db_mgr = DatabaseManager()
        self.server = server

    def get_host(self):
        return self.server.host

    def get_id(self):
        return self.server.get_id()

    def get_leader(self):
        return self.server.get_time_server_host()

    def elect_leader(self):
        return self.server.elect_leader()

    def set_score(self, event_type, score, timestamp):
        return self.db_mgr.set_score(event_type, score, timestamp)

    def get_score(self, event_type):
        return self.db_mgr.get_score(event_type)

    def increment_medal_tally(self, team_name, medal_type, timestamp):
        return self.db_mgr.increment_medal_tally(team_name, medal_type, timestamp)

    def get_medal_tally(self, team_name):
        return self.db_mgr.get_medal_tally(team_name)


    
class DatabaseRPCHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

    def do_POST(self):
        clientIP, clientPort = self.client_address
        print clientIP, clientPort
        SimpleXMLRPCRequestHandler.do_POST(self)

def main(ip, port=8000):
    hosts = [('localhost', 8000), ('localhost', 8001), ('localhost', 8002)] # Fix this... this is simply the hosts of all the three servers
    server = AsyncXMLRPCServer((ip, port), DatabaseRPCHandler, hosts)
    server.register_introspection_functions()
    server.register_instance(DBServerFunctions(server))
    threading.Timer(10, server.check_time_server).start()
    while(1):
        server.handle_request()
        

if __name__ == "__main__":
    main("localhost", 8000) #TODO: Delete me
   
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

