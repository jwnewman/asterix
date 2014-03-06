from threading import Thread, RLock, Event
from Global import Global
from Team import Team
from OlympicEvent import OlympicEvent
import time

TEAMS = ["Gaul", "Rome", "Carthage", "Greece", "Persia"]
MEDALS = ["gold", "silver", "bronze"]
EVENTS = ["Stone Curling", "Stone Skating", "Underwater Stone Weaving", "Synchronized Stone Swimming"]

def synchronized(lock):
    def wrap(f):
        def newFunction(*args, **kw):
            lock.acquire()
            print "Lock acquired. Sleeping."
            time.sleep(10)
            try:
                return f(*args, **kw)
            finally:
                lock.release()
                print "Lock released"
        return newFunction
    return wrap

def synchronized_check(lock):
    def wrap(f):
        def newFunction(*args, **kw):
            while(lock.locked()):
                assert (1==2)
                time.sleep(0.1)
            return f(*args, **kw)
        return newFunction
    return wrap

class ScoreKeeper:
    def __init__(self):
        self.events = {}
        self.teams = {}
        for event_name in EVENTS:
            self.events[event_name.lower()] = OlympicEvent(event_name)
        for team_name in TEAMS:
            self.teams[team_name.lower()] = Team(team_name)

    @synchronized_check(Global.medal_lock)
    def get_medal_tally(self, team_name):
        if team_name.lower() not in [t.lower() for t in TEAMS]:
            return "Error 8483 -- unrecognized team name:\n\t%s"%team_name
        return self.teams[team_name.lower()].get_medal_tally()

    @synchronized(Global.medal_lock)
    def increment_medal_tally(self, team_name, medal_type):
        if medal_type.lower() not in [m.lower() for m in MEDALS]:
            return "Error 15010 -- unrecognized medal metal:\n\t%s"%medal_type
        self.teams[team_name.lower()].increment_medals(medal_type)
        return "Medal tally successfully incremented."

    @synchronized_check(Global.score_lock)
    def get_score(self, event_type):
        if event_type.lower() not in [e.lower() for e in EVENTS]:
            return "Error 28734 -- unrecognized event type:\n\t%s"%event_type
        return self.events[event_type.lower()].get_score()

    @synchronized(Global.score_lock)
    def set_score(self, event_type, score):
        if event_type.lower() not in [e.lower() for e in EVENTS]:
            return "Error 5 -- unrecognized event type:\n\t%s"%event_type
        self.events[event_type.lower()].set_score(score)
        return "Score successfully updated."
    
    @synchronized(Global.client_lock)
    def register_client(self, client_id, events, teams):
        if type(client_id) != int:
            return "Error 29010 -- invalid client id"
        ack = "Successfully registered for: "
        err = "Error in registering for: "
        for event in events:
            if event.lower() in [e.lower() for e in EVENTS]:
                self.events[event.lower()].add_client(client_id)
                ack += "%\ts\n"%event
            else:
                err += "%\ts\n"%event

        for team in teams:
            if team.lower() in [t.lower() for t in TEAMS]:
                self.teams[team.lower()].add_client(client_id)
                ack += "%\ts\n"%team
            else:
                err += "%\ts\n"%team
        return ack + err

    @synchronized_check(Global.client_lock)
    def get_registered_clients_for_event(self, event_type):
        if event_type.lower() not in [e.lower() for e in EVENTS]:
            return "Error 0928 -- unrecognized event type:\n\t%s"%event_type
        return self.events[event_type.lower()].get_clients()

    @synchronized_check(Global.client_lock)
    def get_registered_clients_for_team(self, team_name):
        if team_name.lower() not in [t.lower() for t in TEAMS]:
            return "Error 0273 -- unrecognized team name\n\t%s"%team_name
        return self.teams[team_name.lower()].get_clients()


  
