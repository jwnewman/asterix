import sqlite3
from threading import Thread, RLock, Event
from Global import Global
import datetime

# This wrapper wraps around functions that actually acquire locks. Any function that modifies data will acquire a lock so that no two threads
# can enter this function at once.
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

# This wrapper wraps around functions that must simply wait until a lock is released. The reason for having two different functions is that
# we want methods like get_medal_tally to be able to be accessed asynchronously, UNLESS data modification is happening. This prevents inconsistency.
def synchronized_check(lock):
    def wrap(f):
        def newFunction(*args, **kw):
            while(lock.locked()):
                pass
            return f(*args, **kw)
        return newFunction
    return wrap

class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect('scores.db', check_same_thread = False)
        with self.conn:
            self.cur = self.conn.cursor()
            self.cur.execute("CREATE TABLE IF NOT EXISTS Teams(Name TEXT, Gold_Medals INT, Silver_Medals INT, Bronze_Medals INT, Timestamp TEXT)")
            self.cur.execute("CREATE TABLE IF NOT EXISTS OlympicEvents(Type TEXT, Score TEXT, Timestamp TEXT)")

    def insert_team_into_db(self, team_name):
        team = (team_name, 0, 0, 0, '')
        with self.conn:
            self.cur.execute("INSERT INTO Teams VALUES(?, ?, ?, ?, ?)", team)
        return

    def insert_olympic_event_into_db(self, event_type):
        olympic_event = (event_type, 'No score yet!', '')
        with self.conn:
            self.cur.execute("INSERT INTO OlympicEvents VALUES(?, ?, ?)", olympic_event)
        return

    @synchronized(Global.medal_lock)
    def increment_medal_tally(self, team_name, medal_type, timestamp):
        with self.conn:
            self.cur.execute("SELECT * FROM Teams WHERE Name=?", (team_name,))
            data = self.cur.fetchone()
            if (data is None):
                print "Enter"
                self.insert_team_into_db(team_name)
            if (medal_type == 'gold'):
                self.cur.execute("UPDATE Teams SET Gold_Medals=Gold_Medals+1, Timestamp=? WHERE Name=?", (timestamp, team_name))
            elif (medal_type == 'silver'):
                self.cur.execute("UPDATE Teams SET Silver_Medals=Silver_Medals+1, Timestamp=? WHERE Name=?", (timestamp, team_name))
            elif (medal_type == 'bronze'):
                self.cur.execute("UPDATE Teams SET Bronze_Medals=Bronze_Medals+1, Timestamp=? WHERE Name=?", (timestamp, team_name))
        return "Successfully incremented."

    @synchronized_check(Global.medal_lock)
    def get_medal_tally(self, team_name):
        with self.conn:
            self.cur.execute("SELECT * FROM Teams WHERE Name=?", (team_name,))
            row = self.cur.fetchone()
        return "Team %s has:\n%d gold medals\n%d silver medals\n%d bronze medals\nas of %s\n"%(team_name, row[1], row[2], row[3], row[4])

    @synchronized(Global.score_lock)
    def set_score(self, event_type, score, timestamp):
        with self.conn:
            self.cur.execute("SELECT * FROM OlympicEvents WHERE Type=?", (event_type,))
            data = self.cur.fetchone()
            if (data is None):
                self.insert_olympic_event_into_db(event_type)

            self.cur.execute("UPDATE OlympicEvents SET Score=?, Timestamp=? WHERE Type=?", (score, timestamp, event_type))
        return "Score successfully updated."

    @synchronized_check(Global.score_lock)
    def get_score(self, event_type):
        with self.conn:
            self.cur.execute("SELECT * FROM OlympicEvents WHERE Type=?", (event_type,))
            row = self.cur.fetchone()
        score = row[1]
        timestamp = row[2]
        return score + " ["+timestamp+"]\n"

if __name__ == "__main__":
    db_mgr = DatabaseManager()

    t = datetime.datetime.now().time()
    timestamp = t.strftime('%H:%M:%S')

    db_mgr.increment_medal_tally("Gaul", "gold", timestamp)
    print db_mgr.get_medal_tally("Gaul")
    db_mgr.set_score("Stone Curling", "Gaul is winning!", timestamp)
    print db_mgr.get_score("Stone Curling")
        

    
        