import xmlrpclib
import socket
import time
from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
import random

TEAMS = ["Gaul", "Rome", "Carthage", "Greece", "Persia"]
EVENTS = ["Stone Curling", "Stone Skating", "Underwater Stone Weaving", "Synchronized Stone Swimming"]

class StoneTablet:
    def __init__(self, ip, port, server_ip, server_port, teams=[], events=[]):
        self.id = (ip, port)
        self.teams = teams
        self.events = events
        print "%s:%d"%(server_ip, server_port)
        self.server = xmlrpclib.ServerProxy("%s:%d"%(server_ip, server_port))
        # Latency measurements for client-pull architecture
        self.latencies = []

    # Methods for client-pull architecture

    def get_medal_tally(self, team):
        return self.server.get_medal_tally(team)

    def get_score(self, event):
        return self.server.get_score(event)

    def pull(self):
        for team in self.teams:
            request_time = time.time()
            print self.get_medal_tally(team)
            self.latencies.append(time.time() - request_time)
        for event in self.events:
            request_time = time.time()
            print self.get_score(event)
            self.latencies.append(time.time() - request_time)
        print "--------------------"

    # Methods for server-push architecture

    class ListenerFunctions:
        def print_medal_tally_for_team(self, medal_tally, time_of_update):
            print medal_tally
            return time.time() - time_of_update
        def print_score_for_event(self, score, time_of_update):
            print score
            return time.time() - time_of_update

    def register_with_server(self):
        print self.server.register_client(self.id, self.events, self.teams)
    def serve(self):
        # callback_server = SimpleXMLRPCServer(self.id[0], self.id[1])
        callback_server = SimpleXMLRPCServer(self.id, requestHandler=SimpleXMLRPCRequestHandler)
        callback_server.register_introspection_functions()
        callback_server.register_instance(self.ListenerFunctions())
        self.register_with_server()
        callback_server.serve_forever()

def main(ip, port, teams = ["Gaul"], events = ["Stone Curling"], server_ip='http://localhost', server_port=8000, client_pull=False, pull_rate=5):
    client = StoneTablet(ip, port, server_ip, server_port, teams, events)
    try:
        # Client-pull architecture
        while(client_pull):
            client.pull()
            time.sleep(pull_rate)
            print "*****************"

        # Server-push architecture
        client.serve()
    except KeyboardInterrupt:
        print "\nStopping\n"
        print "Avg. latency: %f"%(float(sum(client.latencies))/(len(client.latencies)+1))
        raise

if __name__ == "__main__":
    # ip = '128.119.40.193'
    ip = 'localhost'
    port = random.randint(8002, 9000)
    num_teams = random.randint(1, len(TEAMS))
    num_events = random.randint(1, len(EVENTS))
    # fav_teams = random.sample(TEAMS, num_teams)
    # fav_events = random.sample(EVENTS, num_events)
    fav_teams = ["Gaul"]
    fav_events = ["Stone Curling"]
    # server_ip = '128.119.40.193'
    server_ip = 'http://localhost'

    main(ip=ip, port=port, server_ip=server_ip, server_port=8000, teams=fav_teams, events=fav_events)




        







