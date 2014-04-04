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
    port -- Int for StoneTablet's port.
    server_ip -- String for IP address for the Pygmy.com server.
    server_port -- Int for Port for the Pygmy.com server.
    """
    def __init__(self, port, server_ip, server_port):
        self.port = port
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

def random_main(port=8001, server_ip='localhost', server_port=8000, update_rate=1):
    """Main method that randomly simulates Olympic games and sends Cacofonix updates to Pygmy.com"""
    fonix = Cacofonix(port = port, server_ip = server_ip, server_port = server_port)
    while(True):
        try:
            # rn.seed(10)
            time.sleep(random.random()*update_rate)
            event = random.randint(0, len(EVENTS)-1)
            team = random.randint(0, len(TEAMS)-1)
            lead = random.randint(1, 100)
            score = create_flavor_statement(team, event, lead)

            fonix.set_score(EVENTS[event], score)

            if random.random() > 0.5:
                medal_winners = random.sample(TEAMS, 3)
                [fonix.increment_medal_tally(team, MEDALS[medal]) for medal, team in enumerate(medal_winners)]
        except (KeyboardInterrupt):
            raise


def test_main(port=8003, server_ip='localhost', server_port=8001, update_rate=1):
    fonix = Cacofonix(port = port, server_ip = server_ip, server_port = server_port)

    fonix.increment_medal_tally("Gaul", "gold")
    """while(True):
        try:
            # rn.seed(10)
            time.sleep(update_rate)
            event = 0
            team = 0
            lead = 1
            score = create_flavor_statement(team, event, lead)

            print score
            fonix.set_score(EVENTS[event], score)

            print "Gaul: gold"
            fonix.increment_medal_tally("Gaul", "gold")
            
        except (KeyboardInterrupt):
            break"""

if __name__ == "__main__":
    test_main()

    """try:
        opts, args = getopt.getopt(sys.argv[1:], "", ["port=", "serip=","serport=","mode=", "rate="])
    except getopt.error, msg:
        print msg
        sys.exit(2)

    port, server_ip, server_port, mode, rate = [x[1] for x in opts]

    if mode == "random":
        random_main(port=int(port), server_ip=server_ip, server_port=int(server_port), update_rate=int(rate))
    elif mode == "testing":
        test_main(port=int(port), server_ip=server_ip, server_port=int(server_port), update_rate=int(rate))
    else:
        raise TypeError"""

    











