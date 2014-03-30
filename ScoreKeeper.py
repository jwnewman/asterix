import xmlrpclib
import socket
from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from Team import Team
from OlympicEvent import OlympicEvent
import datetime

# This class serves as an intermediary between the server that communicates with remote clients, and the data backends (Team and OlympicEvent.)
# This class also takes care of error handling and synchronization.

TEAMS = ["Gaul", "Rome", "Carthage", "Greece", "Persia"]
MEDALS = ["gold", "silver", "bronze"]
EVENTS = ["Stone Curling", "Stone Skating", "Underwater Stone Weaving", "Synchronized Stone Swimming"]

db_server_ip = 'localhost' #TODO: change this
db_server_port = 8000

class ScoreKeeper:
    def __init__(self):
        self.events = {}
        self.teams = {}
        for event_name in EVENTS:
            self.events[event_name.lower()] = OlympicEvent(event_name)
        for team_name in TEAMS:
            self.teams[team_name.lower()] = Team(team_name)
        self.db_server = xmlrpclib.ServerProxy("http://%s:%d"%(db_server_ip, db_server_port))

    def get_medal_tally(self, team_name):
        if team_name.lower() not in [t.lower() for t in TEAMS]:
            return "Error 8483 -- unrecognized team name:\n\t%s"%team_name
        return self.db_server.get_medal_tally(team_name)

    def increment_medal_tally(self, team_name, medal_type, timestamp):
        if medal_type.lower() not in [m.lower() for m in MEDALS]:
            return "Error 15010 -- unrecognized medal metal:\n\t%s"%medal_type
        return self.db_server.increment_medal_tally(team_name, medal_type, timestamp)

    def get_score(self, event_type):
        if event_type.lower() not in [e.lower() for e in EVENTS]:
            return "Error 28734 -- unrecognized event type:\n\t%s"%event_type
        return self.db_server.get_score(event_type)

    def set_score(self, event_type, score, timestamp):
        if event_type.lower() not in [e.lower() for e in EVENTS]:
            return "Error 5 -- unrecognized event type:\n\t%s"%event_type
        return self.db_server.set_score(event_type, score, timestamp)

# All functions below deprecated
    def register_client(self, client_id, events, teams):
        if len(client_id) != 2:
            return "Error 39484 -- invalid client id"
        if type(client_id[0]) != str:
            return "Error 432 -- invalid client id"
        if type(client_id[1]) != int:
            return "Error 940 -- invalid client id"
        ack = "Successfully registered for: \n"
        err = "Error in registering for: \n"
        errors = False
        # Constructing the returned string
        for event in events:
            if event.lower() in [e.lower() for e in EVENTS]:
                self.events[event.lower()].add_client(client_id)
                ack += "\t%s\n"%event
            else:
                err += "\t%s\n"%event
                errors = True

        for team in teams:
            if team.lower() in [t.lower() for t in TEAMS]:
                self.teams[team.lower()].add_client(client_id)
                ack += "\t%s\n"%team
            else:
                err += "\t%s\n"%team
                errors = True
        if not errors:
            return ack
        else:
            return ack + err

    def unregister_client(self, client_id):
        if len(client_id) != 2:
            return "Error 39484 -- invalid client id"
        if type(client_id[0]) != str:
            return "Error 432 -- invalid client id"
        if type(client_id[1]) != int:
            return "Error 940 -- invalid client id"
        for event in EVENTS:
            if client_id in self.events[event.lower()].get_clients():
                self.events[event.lower()].remove_client(client_id)
        for team in TEAMS:
            if client_id in self.teams[team.lower()].get_clients():
                self.teams[team.lower()].remove_client(client_id)

    def get_registered_clients_for_event(self, event_type):
        if event_type.lower() not in [e.lower() for e in EVENTS]:
            print "Error 0928 -- unrecognized event type:\n\t%s"%event_type
            return []
        print self.events[event_type.lower()].get_clients()
        return self.events[event_type.lower()].get_clients()

    def get_registered_clients_for_team(self, team_name):
        if team_name.lower() not in [t.lower() for t in TEAMS]:
            print "Error 0273 -- unrecognized team name\n\t%s"%team_name
            return []
        return self.teams[team_name.lower()].get_clients()

if __name__ == "__main__":
    score_keeper = ScoreKeeper()

    t = datetime.datetime.now().time()
    timestamp = t.strftime('%H:%M:%S')

    print score_keeper.increment_medal_tally("Gaul", "gold", timestamp)
    print score_keeper.get_medal_tally("Gaul")
    print score_keeper.set_score("Stone Curling", "Gaul is winning!", timestamp)
    print score_keeper.get_score("Stone Curling")
        




  
