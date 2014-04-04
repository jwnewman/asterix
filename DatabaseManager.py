"""Module for DatabaseManager and related classes."""

import sqlite3
from threading import Thread, RLock, Event
from Global import Global
import datetime
from Synchronized import synchronized, synchronized_check

class DatabaseManager:
    """DatabaseManager is the interface to SQL database on disk.

    Writes/reads all event scores and medal tallies. 

    Also, keeps track of the raffle entries.
    """
    def __init__(self):
        self.raffle_entries = {}
        self.conn = sqlite3.connect('scores.db', check_same_thread = False)
        with self.conn:
            self.cur = self.conn.cursor()
            self.cur.execute("CREATE TABLE IF NOT EXISTS Teams(Name TEXT, Gold_Medals INT, Silver_Medals INT, Bronze_Medals INT, Timestamp TEXT)")
            self.cur.execute("CREATE TABLE IF NOT EXISTS OlympicEvents(Type TEXT, Score TEXT, Timestamp TEXT)")

    def check_raffle(self, client_id, vector_clock_str):
        print vector_clock_str
        vector_clock = map(int, vector_clock_str.split())
        if sum(vector_clock)%10==0:
            print self.enter_raffle_contestant(client_id, sum(vector_clock))

    @synchronized(Global.raffle_lock)
    def enter_raffle_contestant(self, client_id, entry_num):
        if entry_num not in self.raffle_entries:
            self.raffle_entries[entry_num] = client_id
            return "Successfully entered %s as the %dth contestant!"%(client_id, entry_num)
        else:
            return "No, sorry: %dth contestant already entered."%(entry_num)

    def insert_team_into_db(self, team_name):
        """Performs INSERT into SQL DB of given team name.

        Arguments:
        team_name -- String for one of the Olympic teams.
        """
        team = (team_name, 0, 0, 0, '')
        with self.conn:
            self.cur.execute("INSERT INTO Teams VALUES(?, ?, ?, ?, ?)", team)
        return

    def insert_olympic_event_into_db(self, event_type):
        """Performs INSERT into SQL DB of given event type.

        Arguments:
        event_type -- String for one of the Olympic events.
        """
        olympic_event = (event_type, 'No score yet!', '')
        with self.conn:
            self.cur.execute("INSERT INTO OlympicEvents VALUES(?, ?, ?)", olympic_event)
        return

    @synchronized(Global.medal_lock)
    def increment_medal_tally(self, team_name, medal_type, timestamp):
        """Performs UPDATE into SQL DB for a given team and medal tally.

        Locks on current medal tally.

        Arguments:
        team_name -- String for one of the Olympic teams.
        medal_type -- String for the type of medal to increment.
        timestamp -- Time of the update.
        """
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
        """Returns the current medal tally for a given team via SELECT from SQL DB.

        Locks on medal tally.

        Arguments:
        team_name -- String for one of the Olympic teams.
        """
        with self.conn:
            self.cur.execute("SELECT * FROM Teams WHERE Name=?", (team_name,))
            row = self.cur.fetchone()
        return "Team %s has:\n%d gold medals\n%d silver medals\n%d bronze medals\nas of %s\n"%(team_name, row[1], row[2], row[3], row[4])

    @synchronized(Global.score_lock)
    def set_score(self, event_type, score, timestamp):
        """Performs UPDATE into SQL DB for a given event and score.

        Locks on event score.

        Arguments:
        event_type -- String for one of the Olympic events.
        score -- String for the updated score.
        timestamp -- Time of the update.
        """
        with self.conn:
            self.cur.execute("SELECT * FROM OlympicEvents WHERE Type=?", (event_type,))
            data = self.cur.fetchone()
            if (data is None):
                self.insert_olympic_event_into_db(event_type)

            self.cur.execute("UPDATE OlympicEvents SET Score=?, Timestamp=? WHERE Type=?", (score, timestamp, event_type))
        return "Score successfully updated."

    @synchronized_check(Global.score_lock)
    def get_score(self, event_type):
        """Returns the current score for a given event via SELECT from SQL DB.

        Locks on event score.

        Arguments:
        event_type -- String for one of the Olympic events.
        """
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
        

    
        
