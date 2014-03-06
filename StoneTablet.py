import xmlrpclib
import socket
import time
from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
import random

TEAMS = ["Gaul", "Rome", "Carthage", "Greece", "Persia"]
EVENTS = ["Stone Curling", "Stone Skating", "Underwater Stone Weaving", "Synchronized Stone Swimming"]

class StoneTablet:
    def __init__(self, ip, port, server_ip, server_port, teams=[], events=[]):
        self.id = (ip, port)
        self.teams = teams
        self.events = events
        self.server = xmlrpclib.ServerProxy("%s:%d"%(server_ip, server_port))

    # Methods for client-pull architecture

    def get_medal_tally(self, team):
        return self.server.get_medal_tally(team)

    def get_score(self, event):
        return self.server.get_score(event)

    def pull(self):
        for team in self.teams:
            print self.get_medal_tally(team)
        for event in self.events:
            print self.get_score(event)

    # Methods for server-push architecture

    class ListenerFunctions:
        def print_medal_tally_for_team(self, medal_tally):
            print medal_tally
        def print_score_for_event(self, score):
            print score

    def register_with_server(self):
        print self.server.register_client(client_id=self.id, events=self.events, teams=self.teams)

    def serve(self):
        callback_server = SimpleXMLRPCServer("%s:%d"%(self.get_my_IP(), self.port))
        callback_server.register_introspection_functions()
        self.register_with_server()
        callback_server.serve_forever()

def main(ip, port, teams = ["Gaul"], events = ["Stone Curling"], server_ip='http://localhost', server_port=8000, client_pull = True, pull_rate = 0.0001):
    client = StoneTablet(port, server_ip, server_port, teams, events)

    # Client-pull architecture
    while(client_pull):
        client.pull()
        time.sleep(pull_rate)

    # Server-push architecture
    client.serve()

if __name__ == "__main__":
    ip = '128.119.40.193'
    port = random.randint(8002, 9000)
    num_teams = random.randint(1, len(TEAMS))
    num_events = random.randint(1, len(EVENTS))
    fav_teams = [TEAMS[t] for t in random.sample(len(TEAMS), num_teams)]
    fav_events = [EVENTS[e] for e in random.sample(len(EVENTS), num_events)]
    server_ip = '128.119.40.193'

    main(ip=ip, port=port, server_ip=server_ip, teams=fav_teams, events=fav_events)




        







