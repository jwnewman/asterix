"""Module for ScoreKeeper class."""

import xmlrpclib
import socket
from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from Team import Team
from OlympicEvent import OlympicEvent
import datetime

TEAMS = ["Gaul", "Rome", "Carthage", "Greece", "Persia"]
MEDALS = ["gold", "silver", "bronze"]
EVENTS = ["Stone Curling", "Stone Skating", "Underwater Stone Weaving", "Synchronized Stone Swimming"]

class ScoreKeeper:
    """ScoreKeeper is an intermediary between the client-facing server and the data backend.

    ScoreKeeper supports both server-push and client-pull mode.  
    Server-push mode has been deprecated for Lab #2.

    Arguments:
    db -- (ip, port) tuple which is the address of the database server.
    """
    def __init__(self, db):
        self.cache = {}
        for event_name in EVENTS:
            self.cache[event_name.lower()] = ""
        for team_name in TEAMS:
            self.cache[team_name.lower()] = ""
        self.db = db

    def get_medal_tally(self, team_name, client_id, vector_clock_str):
        """Returns the current medal tally for a given team via RPC to the DB Server.

        Always called by one of the frontend servers on behalf of a requesting client.

        Arguments:
        team_name -- String for one of the Olympic teams.
        client_id -- Unique string ID of the initial requesting client (used for raffle).
        vector_clock_str -- String representation of the vector clock of the frontend server.
        """
        db_server = xmlrpclib.ServerProxy("http://%s:%d"%self.db)
        if team_name.lower() not in [t.lower() for t in TEAMS]:
            return "Error 8483 -- unrecognized team name:\n\t%s"%team_name
        if self.cache[team_name.lower()] == "":
            tally = db_server.get_medal_tally(team_name, client_id, vector_clock_str)
            self.cache[team_name.lower()] = tally
            return tally
        else:
            return self.cache[team_name.lower()]

    def increment_medal_tally(self, team_name, medal_type, timestamp, invalidate_cache=True):
        """Increments the medal tally for a given team via RPC to the DB Server.

        Always called by one of the frontend servers on behalf of a Cacofonix update.

        Arguments:
        team_name -- String for one of the Olympic teams.
        medal_type -- String for the type of medal to increment.
        timestamp -- Time of the update.
        """
        db_server = xmlrpclib.ServerProxy("http://%s:%d"%self.db)
        if medal_type.lower() not in [m.lower() for m in MEDALS]:
            return "Error 15010 -- unrecognized medal metal:\n\t%s"%medal_type
        if invalidate_cache:
            self.cache[team_name.lower()] = ""
        return db_server.increment_medal_tally(team_name, medal_type, timestamp)

    def get_score(self, event_type, client_id, vector_clock_str):
        """Returns the current score for a given event via RPC to the DB Server.

        Always called by one of the frontend servers on behalf of a requesting client.

        Arguments:
        event_type -- String for one of the Olympic events.
        client_id -- Unique string ID of the initial requesting client (used for raffle).
        vector_clock_str -- String representation of the vector clock of the frontend server.
        """
        db_server = xmlrpclib.ServerProxy("http://%s:%d"%self.db)
        if event_type.lower() not in [e.lower() for e in EVENTS]:
            return "Error 28734 -- unrecognized event type:\n\t%s"%event_type

        if self.cache[event_type.lower()] == "":
            score = db_server.get_score(event_type, client_id, vector_clock_str)
            self.cache[event_type.lower()] = score
            return score
        else:
            print self.cache
            return self.cache[event_type.lower()]

    def set_score(self, event_type, score, timestamp, invalidate_cache=True):
        """Sets the score for a given event via RPC to the DB Server.

        Always called by one of the frontend servers on behalf of a Cacofonix update.

        Arguments:
        event_type -- String for one of the Olympic events.
        score -- String for the updated score.
        timestamp -- Time of the update.
        """
        db_server = xmlrpclib.ServerProxy("http://%s:%d"%self.db)
        if event_type.lower() not in [e.lower() for e in EVENTS]:
            return "Error 5 -- unrecognized event type:\n\t%s"%event_type
        if invalidate_cache:
            self.cache[event_type.lower()] = ""
        return db_server.set_score(event_type, score, timestamp)

# --------------------------------------------------------------------
# All functions below are for server-push mode (deprecated for Lab #2).
# --------------------------------------------------------------------

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
    score_keeper = ScoreKeeper(('localhost', 8000))

    t = datetime.datetime.now().time()
    timestamp = t.strftime('%H:%M:%S')

    print score_keeper.increment_medal_tally("Gaul", "gold", timestamp)
    print score_keeper.get_medal_tally("Gaul", "randomclient", "")
    print score_keeper.set_score("Stone Curling", "Gaul is winning!", timestamp)
    print score_keeper.get_score("Stone Curling", "randomclient", "")
  
