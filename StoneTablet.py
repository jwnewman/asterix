"""Module for the StoneTable class."""

import xmlrpclib
import socket
import time
from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
import random
import sys 
import getopt
import os

TEAMS = ["Gaul", "Rome", "Carthage", "Greece", "Persia"]
EVENTS = ["Stone Curling", "Stone Skating", "Underwater Stone Weaving", "Synchronized Stone Swimming"]


class StoneTablet:
    """StoneTablet is the app that clients run on their SmartStones.

    StoneTablet supports both server-push and client-pull mode.
    Server-push mode has been deprecated for Lab #2.

    Arguments:
    ip -- String for StoneTablets's IP address.
    port -- Int for StoneTablet's port.
    server_ip -- String for IP address for the Pygmy.com server.
    server_port -- Int for Port for the Pygmy.com server.
    teams -- List of team names to register for pull or push updates.
    events -- List of events to register for pull or push updates.
    """
    def __init__(self, ip, port, server_ip, server_port, teams=[], events=[]):
        self.id = (ip, port)
        self.str_id = "%s:%d"%self.id
        self.teams = teams
        self.events = events
        self.server = xmlrpclib.ServerProxy("http://%s:%d"%(server_ip, server_port))
        # -----------------------------------------------------------
        # Below are logging and latency vars (deprecated for Lab #2).
        # -----------------------------------------------------------
        if not os.path.exists("client_logs"):
            os.makedirs("client_logs")
        self.log_file = open("client_logs/%d.txt"%port, "w+", 5)

        if not os.path.exists("latencies"):
            os.makedirs("latencies")
        self.latency_file = open("latencies/%d.txt"%port, "w+", 5)
        self.last_update = None
    
    def get_medal_tally(self, team_name):
        """Returns the current medal tally for a given team via RPC to Pygmy.com.

        Arguments:
        team_name -- String for one of the Olympic teams.
        """
        return self.server.get_medal_tally(team_name, self.str_id)

    def get_score(self, event_type):
        """Returns the current score for a given event via RPC to Pygmy.com.

        Arguments:
        event_type -- String for one of the Olympic events.
        """
        return self.server.get_score(event_type, self.str_id)

    def pull(self):
        """Performs a client-pull for updates on all of the teams and events the client follows.

        Prints all updates to the console and also writes them to a log.        
        """
        if self.last_update is None:
            self.log_file.write("\nLoading data...\n\n")
        else:
            self.log_file.write("\nRefreshing... last update: %s\n\n"%time.strftime("%d %b %Y %H:%M:%S", time.gmtime()))
        self.log_file.write("-------LATEST MEDAL TALLY FOR TEAMS YOU FOLLOW-------\n")
        for team in self.teams:
            request_time = time.time()
            medal_update = self.get_medal_tally(team)
            print medal_update
            self.log_file.write("%s\n"%medal_update)
            latency=time.time() - request_time
            self.latency_file.write("%f\n"%latency)
        self.log_file.write("-------LATEST SCORE FOR EVENTS YOU FOLLOW-------\n")
        for event in self.events:
            request_time = time.time()
            score_update = self.get_score(event)
            print score_update
            self.log_file.write("%s\n"%score_update)
            latency=time.time() - request_time
            self.latency_file.write("%f\n"%latency)
        self.last_update = time.strftime("%d %b %Y %H:%M:%S", time.gmtime())

# --------------------------------------------------------------------
# All functions below are for server-push mode (deprecated for Lab #2).
# --------------------------------------------------------------------

    class ListenerFunctions:
        """RPC interface for the server to call in server-push mode.

        Deprecated for Lab #2.

        Arguments:
        log_file -- Opened file for logging updates. 
        latency_file -- Opened file for logging latecies.
        """
        def __init__(self, log_file, latency_file):
            self.log_file = log_file
            self.latency_file = latency_file

        def print_medal_tally_for_team(self, medal_tally, time_of_update):
            """Prints and logs medal update from server."""
            print medal_tally
            latency = time.time() - time_of_update
            self.log_file.write("-------BREAKING NEWS: %s-------\n"%time.strftime("%d %b %Y %H:%M:%S", time.gmtime()))
            self.log_file.write("%s\n\n"%medal_tally)
            self.latency_file.write("%f\n"%latency)
            return latency

        def print_score_for_event(self, score, time_of_update):
            """Prints and logs score update from server."""
            print score
            latency = time.time() - time_of_update
            self.log_file.write("-------BREAKING NEWS: %s-------\n"%time.strftime("%d %b %Y %H:%M:%S", time.gmtime()))
            self.log_file.write("%s\n\n"%score)
            self.latency_file.write("%f\n"%latency)
            return latency

    def register_with_server(self):
        """Registers events and teams the client follows with server for server-push updates."""
        print self.server.register_client(self.id, self.events, self.teams)
        self.server.register_client(self.id, self.events, self.teams)

    def serve(self):
        """Serves for server-push mode.

        Registers with servers and listens for updates. 
        """
        available_port = False
        while (not available_port):
            try:
                callback_server = SimpleXMLRPCServer(self.id, requestHandler=SimpleXMLRPCRequestHandler)
                available_port = True
            except socket.error as err:
                self.id = (self.id[0], random.randint(8005, 9000))

        callback_server.register_introspection_functions()
        callback_server.register_instance(self.ListenerFunctions(self.log_file, self.latency_file))
        self.register_with_server()
        callback_server.serve_forever()

def main(ip, port, teams = ["Gaul"], events = ["Stone Curling"], server_ip='localhost', server_port=8001, client_pull=True, pull_rate=10):
    client = StoneTablet(ip, port, server_ip, server_port, teams, events)

    print client.get_medal_tally("Gaul")
    """try:
        # Client-pull architecture
        while(client_pull):
            client.pull()
            time.sleep(pull_rate)

        # Server-push architecture
        client.serve()
    except KeyboardInterrupt:
        raise"""

if __name__ == "__main__":

    main('localhost', 8005)
    # main(ip=ip, port=port, server_ip=server_ip, server_port=8001, teams=fav_teams, events=fav_events)
    #main(ip=ip, port=int(port), teams=fav_teams, events=fav_events, server_ip=server_ip, server_port=int(server_port), client_pull=client_pull)



        







