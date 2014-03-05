from threading import Thread, RLock
from Global import Global
from Team import Team
from Event import Event

def synchronized(lock):
    def wrap(f):
        def newFunction(*args, **kw):
            lock.acquire()
            try:
                return f(*args, **kw)
            finally:
                lock.release()
        return newFunction
    return wrap

class ScoreKeeper:

    def __init__(self, event_names, team_names):
        self.events = {}
        self.teams = {}
        self.medals = ["gold", "silver", "bronze"]
        for event_name in event_names:
            self.events[event_name] = Event(event_name)
        for team_name in team_names:
            self.teams[team_name] = Team(team_name)

    # @synchronized(Global.lock)
    def get_medal_tally(self, team_name):
        return self.teams[team_name].get_medal_tally()

    @synchronized(Global.lock)
    def increment_medal_tally(self, team_name, medal_type):
        if (medal_type.lower() not in self.medals):
            return "Unrecognized medal type."
        self.teams[team_name].increment_medals(medal_type)
        return "Successfully incremented."

        # if (medal_type.lower() == "gold"):
        #     self.teams[team_name].increment_gold_medals()
        # elif (medal_type.lower() == "silver"):
        #     self.teams[team_name].increment_silver_medals()
        # elif (medal_type.lower() == "bronze"):
        #     self.teams[team_name].increment_silver_medals()
        # else:
        #     return "Unrecognized medal type."
        # return "Successfully incremented."

    @synchronized(Global.lock)
    def get_score(self, event_type):
        return self.events[event_type].get_score()

    @synchronized(Global.lock)
    def set_score(self, event_type, score):
        self.events[event_type].set_score(score)
        return


  
