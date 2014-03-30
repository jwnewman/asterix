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

# StoneTablet is the app that clients will run on their SmartStones. Each client can parameterize their StoneTablet with a list of teams and events of interest.
# If no parameters are provided, these will be selected randomly. The client also measures the latency from the server in receiving their request.

class StoneTablet:
    def __init__(self, ip, port, server_ip, server_port, teams=[], events=[]):
        self.id = (ip, port)
        self.teams = teams
        self.events = events
        # print "%s:%d"%(server_ip, server_port)
        self.server = xmlrpclib.ServerProxy("http://%s:%d"%(server_ip, server_port))
        # Log file for output statements
        if not os.path.exists("client_logs"):
            os.makedirs("client_logs")
        self.log_file = open("client_logs/%d.txt"%port, "w+", 5)
        # Latency measurements for client-pull architecture
        if not os.path.exists("latencies"):
            os.makedirs("latencies")
        self.latency_file = open("latencies/%d.txt"%port, "w+", 5)
        self.last_update = None

    # Methods for client-pull architecture
    
    # This function polls the server for the most recent medal_tally for the provided team.
    def get_medal_tally(self, team):
        return self.server.get_medal_tally(team)

    # This function polls the server for the most recent score for the provided event.
    def get_score(self, event):
        return self.server.get_score(event)

    # Polls the server for all of the latest scores and tallies for the events and teams that the StoneTablet follows.
    def pull(self):
        if self.last_update is None:
            self.log_file.write("\nLoading data...\n\n")
        else:
            self.log_file.write("\nRefreshing... last update: %s\n\n"%time.strftime("%d %b %Y %H:%M:%S", time.gmtime()))
        self.log_file.write("-------LATEST MEDAL TALLY FOR TEAMS YOU FOLLOW-------\n")
        for team in self.teams:
            request_time = time.time()
            medal_update = self.get_medal_tally(team)
            # print medal_update
            self.log_file.write("%s\n"%medal_update)
            latency=time.time() - request_time
            self.latency_file.write("%f\n"%latency)
        self.log_file.write("-------LATEST SCORE FOR EVENTS YOU FOLLOW-------\n")
        for event in self.events:
            request_time = time.time()
            score_update = self.get_score(event)
            # print score_update
            self.log_file.write("%s\n"%score_update)
            latency=time.time() - request_time
            self.latency_file.write("%f\n"%latency)
        self.last_update = time.strftime("%d %b %Y %H:%M:%S", time.gmtime())

    # Methods for server-push architecture

    # RPC interface for the server to call in server-push mode.
    class ListenerFunctions:
        def __init__(self, log_file, latency_file):
            self.log_file = log_file
            self.latency_file = latency_file
        # Receives a medal tally from the server and displays it
        def print_medal_tally_for_team(self, medal_tally, time_of_update):
            # print medal_tally
            latency = time.time() - time_of_update
            self.log_file.write("-------BREAKING NEWS: %s-------\n"%time.strftime("%d %b %Y %H:%M:%S", time.gmtime()))
            self.log_file.write("%s\n\n"%medal_tally)
            self.latency_file.write("%f\n"%latency)
            return latency
        # Recieves a score from the server and displays it.
        def print_score_for_event(self, score, time_of_update):
            # print score
            latency = time.time() - time_of_update
            self.log_file.write("-------BREAKING NEWS: %s-------\n"%time.strftime("%d %b %Y %H:%M:%S", time.gmtime()))
            self.log_file.write("%s\n\n"%score)
            self.latency_file.write("%f\n"%latency)
            return latency

    # Sends information to the server about this client so that it can be registered for teams and events of interest.
    def register_with_server(self):
        # print self.server.register_client(self.id, self.events, self.teams)
        self.server.register_client(self.id, self.events, self.teams)

    # Server push mode: Registers with the server and then listens for updates from the server.
    def serve(self):
        available_port = False
        while (not available_port):
            try:
                callback_server = SimpleXMLRPCServer(self.id, requestHandler=SimpleXMLRPCRequestHandler)
                available_port = True
            except socket.error as err:
                self.id = (self.id[0], random.randint(8002, 9000))

        callback_server.register_introspection_functions()
        callback_server.register_instance(self.ListenerFunctions(self.log_file, self.latency_file))
        self.register_with_server()
        callback_server.serve_forever()

def main(ip, port, teams = ["Gaul"], events = ["Stone Curling"], server_ip='localhost', server_port=8001, client_pull=True, pull_rate=10):
    client = StoneTablet(ip, port, server_ip, server_port, teams, events)
    try:
        # Client-pull architecture
        while(client_pull):
            client.pull()
            time.sleep(pull_rate)

        # Server-push architecture
        client.serve()
    except KeyboardInterrupt:
        raise

if __name__ == "__main__":

    main('localhost', 8002)


    # main(ip=ip, port=port, server_ip=server_ip, server_port=8000, teams=fav_teams, events=fav_events)
    main(ip=ip, port=int(port), teams=fav_teams, events=fav_events, server_ip=server_ip, server_port=int(server_port), client_pull=client_pull)



        







