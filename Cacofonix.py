import xmlrpclib
import random
import time

# This class provides the server with real-time updates about Olympic teams and events.

from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler

TEAMS = ["Gaul", "Rome", "Carthage", "Greece", "Persia"]
MEDALS = ["gold", "silver", "bronze"]
EVENTS = ["Stone Curling", "Stone Skating", "Underwater Stone Weaving", "Synchronized Stone Swimming"]
UNITS = ["points", "laps", "baskets", "points"]

# Creates the message that is sent back to the server.
def create_flavor_statement(team, event, lead):
    # TODO: Make more variants

    return "What a day in %s! Currently in the lead is %s by %d %s."%(EVENTS[event].lower(), TEAMS[team], lead, UNITS[event])

class Cacofonix:
    # Cacofonix needs to know the server IP and port, and the secret password which only Cacofonix and the server know.
    def __init__(self, port, server_ip, server_port):
        self.port = port
        self.secret_id = "SECRET PASSWORD LOL HOORAY"
        self.server = xmlrpclib.ServerProxy("%s:%d"%(server_ip, server_port))
        # Latency measurements for server-push architecture
        self.log_file = open("log_cacofonix.txt", "w+")
    # Calls the server with an updated score for an event, gets an acknowledgment back.
    def set_score(self, event, score):
        self.log_file.write("------Received Olympic Event Update: %s------\n"%time.strftime("%d %b %Y %H:%M:%S", time.gmtime()))
        # TODO get back ack/error
        ack = self.server.set_score(event, score, self.secret_id)
        print ack
        self.log_file.write("%s\n"%ack)
    # Calls the server to increment the medal tally, gets an acknowledgment back.
    def increment_medal_tally(self, team, medal):
        self.log_file.write("------Received Olympic Medal Update: %s------\n"%time.strftime("%d %b %Y %H:%M:%S", time.gmtime()))
        # TODO get back ack/error
        ack = self.server.increment_medal_tally(team, medal, self.secret_id)
        print ack
        self.log_file.write("%s\n"%ack)

def random_main(port=8001, server_ip='http://localhost', server_port=8000, update_rate=4):
    fonix = Cacofonix(port = port, server_ip = server_ip, server_port = server_port)
    # Sends updates to the server infinitely with a randomly spaced amount of time in between.
    # Increments the medal tally for a random team about half as often as it sets the score for an event.
    while(True):
        try:
            # rn.seed(10)
            time.sleep(random.randint(0,update_rate))
            event = random.randint(0, len(EVENTS)-1)
            team = random.randint(0, len(TEAMS)-1)
            lead = random.randint(1, 100)
            score = create_flavor_statement(team, event, lead)

            print score
            fonix.set_score(EVENTS[event], score)

            if random.random() > 0.5:
                medal_winners = random.sample(TEAMS, 3)
                print medal_winners
                [fonix.increment_medal_tally(team, MEDALS[medal]) for medal, team in enumerate(medal_winners)]
        except (KeyboardInterrupt):
            raise


def test_main(port=8001, server_ip='http://localhost', server_port=8000, update_rate=4):
    fonix = Cacofonix(port = port, server_ip = server_ip, server_port = server_port)
    while(True):
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
            break



if __name__ == "__main__":
    test_main()











