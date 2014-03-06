#!/usr/bin/env python

import xmlrpclib
import SocketServer
from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from threading import Thread, RLock
from ScoreKeeper import ScoreKeeper
from Global import Global

HOST_NAME = 'http://localhost:'

class AsyncXMLRPCServer(SocketServer.ThreadingMixIn,SimpleXMLRPCServer): pass

class ScoreKeeperFunctions:
    def __init__(self):
        self.keeper = ScoreKeeper()

    def get_medal_tally(self, team_name):
        return self.keeper.get_medal_tally(team_name)
    def increment_medal_tally(self, team_name, medal_type):
        return self.keeper.increment_medal_tally(team_name, medal_type)
    def get_score(self, event_type):
        return self.keeper.get_score(event_type)
    def set_score(self, event_type, score):
        ack = self.keeper.set_score(event_type, score)
        self.push_update(self.keeper.get_registered_clients_for_event(event_type), event_type)
        return ack
    def register_client(self, client_id, events, teams):
        return self.keeper.register_client(client_id, events, teams)
    def push_update(self, clients, event_type):
        for client_id in clients:
            s = xmlrpclib.ServerProxy(HOST_NAME + str(client_id))
            s.print_score_for_event(self.keeper.get_score(event_type))
        return

class ObelixRPCHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

    def do_POST(self):
        clientIP, clientPort = self.client_address
        print clientIP, clientPort
        SimpleXMLRPCRequestHandler.do_POST(self)


# Create server
server = AsyncXMLRPCServer(("localhost", 8000),
                            requestHandler=ObelixRPCHandler)
server.register_introspection_functions()

server.register_instance(ScoreKeeperFunctions())

server.serve_forever()
