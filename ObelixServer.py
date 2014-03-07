#!/usr/bin/env python

import xmlrpclib
import SocketServer
from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from threading import Thread, RLock
from ScoreKeeper import ScoreKeeper
from Global import Global
import socket
import time

# HOST_NAME = '128.119.40.193'
HOST_NAME = 'localhost'
# HOST_NAME = socket.gethostbyname(socket.gethostname())

class AsyncXMLRPCServer(SocketServer.ThreadingMixIn,SimpleXMLRPCServer): pass

class ObelixServerFunctions:
    def __init__(self):
        self.keeper = ScoreKeeper()
        self.secret_id = "SECRET PASSWORD LOL HOORAY"

    def get_medal_tally(self, team_name):
        return self.keeper.get_medal_tally(team_name)
    def increment_medal_tally(self, team_name, medal_type, password):
        if password != self.secret_id:
            return "Unauthorized entry attempt."
        ack = self.keeper.increment_medal_tally(team_name, medal_type)
        latencies = self.push_update_for_team(self.keeper.get_registered_clients_for_team(team_name), team_name)
        return ack, latencies
    def get_score(self, event_type):
        return self.keeper.get_score(event_type)
    def set_score(self, event_type, score, password):
        if password != self.secret_id:
            return "Unauthorized entry attempt."
        ack = self.keeper.set_score(event_type, score)
        latencies = self.push_update_for_event(self.keeper.get_registered_clients_for_event(event_type), event_type)
        return ack, latencies
    def register_client(self, client_id, events, teams):
        return self.keeper.register_client(client_id, events, teams)
    def push_update_for_event(self, clients, event_type):
        latencies = []
        time_of_update = time.time()
        for client_id in clients:
            print client_id
            client_ip, client_port = client_id
            s = xmlrpclib.ServerProxy("http://%s:%d"%(client_ip, client_port))
            try:
                latency = s.print_score_for_event(self.keeper.get_score(event_type), time_of_update)
                print latency
                latencies.append(latency)
            except socket.error as err:
                print "Unable to reach http://%s:%d, unsubscribing."%(client_ip, client_port)
                self.keeper.unregister_client(client_id)
                pass
        return latencies

    def push_update_for_team(self, clients, team_name):
        latencies = []
        time_of_update = time.time()
        for client_id in clients:
            print client_id
            client_ip, client_port = client_id
            s = xmlrpclib.ServerProxy("http://%s:%d"%(client_ip, client_port))
            try:
                latency = s.print_medal_tally_for_team(self.keeper.get_medal_tally(team_name), time_of_update)
                print latency
                latencies.append(latency)
            except socket.error as err:
                print "Unable to reach http://%s:%d, unsubscribing."%(client_ip, client_port)
                self.keeper.unregister_client(client_id)
                pass 
        return latencies

class ObelixRPCHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

    def do_POST(self):
        clientIP, clientPort = self.client_address
        print clientIP, clientPort
        SimpleXMLRPCRequestHandler.do_POST(self)

def main(ip, port=8000):
    server = AsyncXMLRPCServer((ip, port), requestHandler=ObelixRPCHandler)
    server.register_introspection_functions()
    server.register_instance(ObelixServerFunctions())
    server.serve_forever()

if __name__ == "__main__":
    main(ip = HOST_NAME, port=8000)