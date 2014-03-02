#!/usr/bin/env python

from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from threading import Thread, RLock
from ScoreKeeper import ScoreKeeper
from Global import Global

class ScoreKeeperFunctions:
    def get_medal_tally(self, team_name):
        return keeper.get_medal_tally(team_name)
    def increment_medal_tally(self, team_name, medal_type):
        return keeper.increment_medal_tally(team_name, medal_type)
    def get_score(self, event_type):
        return keeper.get_score(self, event_type)
    def set_score(self, event_type):
        return keeper.set_score(self, event_type, score)

class ObelixRPCHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)


# Create server
server = SimpleXMLRPCServer(("localhost", 8000),
                            requestHandler=ObelixRPCHandler)
server.register_introspection_functions()

events = ["Stone Curling", "Stone Skating", "Underwater Stone Weaving"]
teams = ["Gaul", "Rome"]

keeper = ScoreKeeper(events, teams)


server.register_instance(ScoreKeeperFunctions())

server.serve_forever()
