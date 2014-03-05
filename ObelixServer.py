#!/usr/bin/env python

from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from threading import Thread, RLock
from ScoreKeeper import ScoreKeeper
from Global import Global

class ScoreKeeperFunctions:
    def __init__(self):
        self.events = ["Stone Curling", "Stone Skating", "Underwater Stone Weaving"]
        self.teams = ["Gaul", "Rome"]
        self.keeper = ScoreKeeper(self.events, self.teams)

    def get_medal_tally(self, team_name):
        return self.keeper.get_medal_tally(team_name)
    def increment_medal_tally(self, team_name, medal_type):
        return self.keeper.increment_medal_tally(team_name, medal_type)
    def get_score(self, event_type):
        return self.keeper.get_score(self, event_type)
    def set_score(self, event_type):
        return self.keeper.set_score(self, event_type, score)

class ObelixRPCHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

    def do_POST(self):
        clientIP, clientPort = self.client_address
        print clientIP, clientPort
        SimpleXMLRPCRequestHandler.do_POST(self)


# Create server
server = SimpleXMLRPCServer(("localhost", 8000),
                            requestHandler=ObelixRPCHandler)
server.register_introspection_functions()

server.register_instance(ScoreKeeperFunctions())

server.serve_forever()
