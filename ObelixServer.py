#!/usr/bin/env python
"""Module for ObelixServer and related classes."""

import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from AsyncXMLRPCServer import AsyncXMLRPCServer
from ServerFunctions import ServerFunctions
from threading import Lock, Timer
from ScoreKeeper import ScoreKeeper
from Global import Global
import socket
import time
import getopt
import os
import sys

HOST_NAME = 'localhost'

class ObelixServerFunctions(ServerFunctions):
    def __init__(self, log_file, server, db):
        self.keeper = ScoreKeeper(db)
        self.secret_id = "SECRET PASSWORD LOL HOORAY"
        self.log_file = log_file
        ServerFunctions.__init__(self, server)

    def get_medal_tally(self, team_name, client_id):
        self.server.increment_event_count()
        vector_clock_str, medal_tally = self.keeper.get_medal_tally(team_name, client_id, self.server.vector_clock_to_string())
        self.server.sync_vector_clocks(vector_clock_str)
        return medal_tally

    def increment_medal_tally(self, team_name, medal_type, password):
        if password != self.secret_id:
            return "Unauthorized entry attempt."
        ack = self.keeper.increment_medal_tally(team_name, medal_type, self.get_timestamp())
        self.push_update_for_team(self.keeper.get_registered_clients_for_team(team_name), team_name)
        return ack

    def get_score(self, event_type, client_id):
        self.server.increment_event_count()
        vector_clock_str, score = self.keeper.get_score(event_type, client_id, self.server.vector_clock_to_string())
        self.server.sync_vector_clocks(vector_clock_str)
        return score

    def set_score(self, event_type, score, password):
        if password != self.secret_id:
            return "Unauthorized entry attempt."
        ack = self.keeper.set_score(event_type, score, self.get_timestamp())
        self.push_update_for_event(self.keeper.get_registered_clients_for_event(event_type), event_type)
        return ack

    def register_client(self, client_id, events, teams):
        return self.keeper.register_client(client_id, events, teams)

    def push_update_for_event(self, clients, event_type):
        if len(clients)==0:
            return 0
        self.log_file.write("----PUSHING NEW EVENT UPDATE: %s----\n"%time.strftime("%d %b %Y %H:%M:%S", time.gmtime()))
        time_of_update = time.time() # Measure latency

        for client_id in clients:
            client_ip, client_port = client_id
            s = xmlrpclib.ServerProxy("http://%s:%d"%(client_ip, client_port))

            try:
                s.print_score_for_event(self.keeper.get_score(event_type), time_of_update)
                self.log_file.write("Successfully reached http://%s:%d\n"%(client_ip, client_port))
            except socket.error as err:
                self.log_file.write("Unable to reach http://%s:%d, unsubscribing.\n"%(client_ip, client_port))
                self.keeper.unregister_client(client_id)
        return 1

    def push_update_for_team(self, clients, team_name):
        if len(clients)==0:
            return 0
        self.log_file.write("----PUSHING NEW EVENT UPDATE: %s----\n"%time.strftime("%d %b %Y %H:%M:%S", time.gmtime()))
        time_of_update = time.time() # Measure latency

        for client_id in clients:
            client_ip, client_port = client_id
            s = xmlrpclib.ServerProxy("http://%s:%d"%(client_ip, client_port))

            try:
                s.print_medal_tally_for_team(self.keeper.get_medal_tally(team_name), time_of_update)
                self.log_file.write("Successfully reached http://%s:%d\n"%(client_ip, client_port))
            except socket.error as err:
                self.log_file.write("Unable to reach http://%s:%d, unsubscribing.\n"%(client_ip, client_port))
                self.keeper.unregister_client(client_id)
        return 1


class ObelixRPCHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

    def do_POST(self):
        clientIP, clientPort = self.client_address
        print clientIP, clientPort
        SimpleXMLRPCRequestHandler.do_POST(self)

def main(ip, port=8002, uid=1):
    log_file = open("log_server.txt", "w+", 5)
    hosts = [('localhost', 8000), ('localhost', 8002), ('localhost', 8003)] # Fix this... this is simply the hosts of all the three servers
    server = AsyncXMLRPCServer(uid, ObelixRPCHandler, hosts)
    server.register_introspection_functions()
    server.register_instance(ObelixServerFunctions(log_file, server, hosts[0]))
    t = Timer(10, server.check_time_server)
    t.daemon = True
    t.start()
    server.serve_forever()

if __name__ == "__main__":
    # main('localhost', 8003, 2)
    local = False
    try:
        opts, args = getopt.getopt(sys.argv[1:], "lp:i:", ["run_locally","serport=","uid="])
    except getopt.error, msg:
        print msg
        sys.exit(2)
    for o, a in opts:
        if o in ("-h", "--help"):
            print __doc__
            sys.exit(0)
        elif o in ("-l", "--run_locally"):
            local = True
        elif o in ("-p", "--serport"):
            port = int(a)
        elif o in ("-i", "--uid"):
            uid = int(a)
    if local:
        ip = "localhost"
    else:
        ip = socket.gethostbyname(socket.gethostname())
    main(ip=ip, port=port, uid=uid)
