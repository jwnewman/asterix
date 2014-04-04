"""Module for Cacofonix class."""

import xmlrpclib
import random
import time
import getopt
import os
import sys

from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler

TEAMS = ["Gaul", "Rome", "Carthage", "Greece", "Persia"]
MEDALS = ["gold", "silver", "bronze"]
EVENTS = ["Stone Curling", "Stone Skating", "Underwater Stone Weaving", "Synchronized Stone Swimming"]
UNITS = ["points", "laps", "baskets", "points"]

def create_flavor_statement(team_num, event_num, lead):
    """Creates a message that is sent back to the server.

    The returned flavor message is the ``score''. 

    Arguments:
    team_num -- Index (int) in TEAMS for team name.
    event_num -- Index (int) in EVENTS for event type.
    lead -- An int representing how much the team is winning by.
    """
    return "What a day in %s! Currently in the lead is %s by %d %s."%(EVENTS[event_num].lower(), TEAMS[team_num], lead, UNITS[event_num])

class Cacofonix:
    """Cacofonix real-time updates about Olympic teams and events to Pygmy.com.

    Arguments:
    server_ip -- String for IP address for the Pygmy.com server.
    server_port -- Int for Port for the Pygmy.com server.
    """
    def __init__(self, server_ip, server_port):
        self.secret_id = "SECRET PASSWORD LOL HOORAY"
        self.server = xmlrpclib.ServerProxy("http://%s:%d"%(server_ip, server_port))
        self.log_file = open("log_cacofonix.txt", "w+", 5)

    def set_score(self, event_type, score):
        """Sets the score for a given event via RPC to Pygmy.com.

        Passes the secret password to Pygmy.com for Cacofonix authentication.

        Arguments:
        event_type -- String for one of the Olympic events.
        score -- String for the updated score.
        """
        self.log_file.write("------Received Olympic Event Update: %s------\n"%time.strftime("%d %b %Y %H:%M:%S", time.gmtime()))
        ack = self.server.set_score(event_type, score, self.secret_id)
        print ack
        self.log_file.write("%s\n"%ack)

    def increment_medal_tally(self, team_name, medal_type):
        """Increments the medal tally for a given team via RPC to Pygmy.com.

        Passes the secret password to Pygmy.com for Cacofonix authentication.

        Arguments:
        team_name -- String for one of the Olympic teams.
        medal_type -- String for the type of medal to increment.
        """
        self.log_file.write("------Received Olympic Medal Update: %s------\n"%time.strftime("%d %b %Y %H:%M:%S", time.gmtime()))
        ack = self.server.increment_medal_tally(team_name, medal_type, self.secret_id)
        print ack
        self.log_file.write("%s\n"%ack)

def main(server_ip='localhost', server_port=8000, update_rate=5):
    """Main method that randomly simulates Olympic games and sends Cacofonix updates to Pygmy.com"""
    fonix = Cacofonix(server_ip = server_ip, server_port = server_port)
    while(True):
        try:
            time.sleep(random.random()*update_rate)
            event = random.randint(0, len(EVENTS)-1)
            team = random.randint(0, len(TEAMS)-1)
            lead = random.randint(1, 100)
            score = create_flavor_statement(team, event, lead)

            fonix.set_score(EVENTS[event].lower(), score)

            if random.random() > 0.5:
                medal_winners = random.sample(TEAMS, 3)
                [fonix.increment_medal_tally(team.lower(), MEDALS[medal].lower()) for medal, team in enumerate(medal_winners)]
        except (KeyboardInterrupt):
            raise

if __name__ == "__main__":
    local = False
    try:
        opts, args = getopt.getopt(sys.argv[1:], "li:p:", ["run_locally","serip=","serport="])
    except getopt.error, msg:
        print msg
        sys.exit(2)
    for o, a in opts:
        if o in ("-h", "--help"):
            print __doc__
            sys.exit(0)
        elif o in ("-l", "--run_locally"):
            local = True
        elif o in ("-i", "--serip"):
            server_ip = a
        elif o in ("-p", "--serport"):
            server_port = int(a)
    if local:
        server_ip = "localhost"
        server_port = 8001
        
    main(server_ip=server_ip, server_port=server_port)
