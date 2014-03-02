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

    def __init__(self, eventNames, teamNames):
        self.events = []
        self.teams = []
        for eventName in eventNames:
            self.events.append(Event(eventName))
        for teamName in teamNames:
            self.teams.append(Team(teamName))

    @synchronized(Global.lock)
    def get_medal_tally(self, team_name):
        return "2 medals"

    @synchronized(Global.lock)
    def increment_medal_tally(self, team_name, medal_type):
        return

    @synchronized(Global.lock)
    def get_score(self, event_type):
        return

    @synchronized(Global.lock)
    def set_score(self, event_type):
        return


  
