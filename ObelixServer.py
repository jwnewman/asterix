#!/usr/bin/env python

import xmlrpclib
import SocketServer
from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from threading import Thread, RLock
from ScoreKeeper import ScoreKeeper
from Global import Global
import socket
import time

HOST_NAME = 'localhost' # The system is assumed to be running locally. To run across machines, use the line below.
# HOST_NAME = socket.gethostbyname(socket.gethostname())

class AsyncXMLRPCServer(SocketServer.ThreadingMixIn,SimpleXMLRPCServer): pass # Subclassing the SimpleXMLRPCServer to allow it to be threaded

# The following defines the ObelixServer RPC interface
class ObelixServerFunctions:
    def __init__(self, log_file):
        self.keeper = ScoreKeeper() # Create the ScoreKeeper - this is what deals with the data the server keeps.
        self.secret_id = "SECRET PASSWORD LOL HOORAY" # This secret password is known only by ObelixServer and Cacofonix. It allows Cacofonix to set scores and medal tallies.
        self.log_file = log_file

    # A StoneTablet in client pull mode can call this to retrieve the current medal tally for a team with name team_name.
    def get_medal_tally(self, team_name):
        return self.keeper.get_medal_tally(team_name)
    # Cacofonix can call this to increment the medal tally for a certain medal type and a specific team name. This is secured with the secret Cacofonix password.
    def increment_medal_tally(self, team_name, medal_type, password):
        if password != self.secret_id:
            return "Unauthorized entry attempt."
        ack = self.keeper.increment_medal_tally(team_name, medal_type)
        self.push_update_for_team(self.keeper.get_registered_clients_for_team(team_name), team_name) # Immediately update all StoneTablets registered to receive updates for this team.
        return ack
    # A StoneTablet in client pull mode can call this to retrieve the current score for a specific event_type.
    def get_score(self, event_type):
        return self.keeper.get_score(event_type)
    # Cacofonix can call this to set the current score for a specific event. Secured with the Cacofonix password.
    def set_score(self, event_type, score, password):
        if password != self.secret_id:
            return "Unauthorized entry attempt."
        ack = self.keeper.set_score(event_type, score)
        self.push_update_for_event(self.keeper.get_registered_clients_for_event(event_type), event_type) # Immediately update all StoneTablets registered to receive updates for this event.
        return ack
    # A StoneTablet in server push mode calls this to register itself to receive updates for a list of teams and events.
    def register_client(self, client_id, events, teams):
        return self.keeper.register_client(client_id, events, teams)
    # Updates clients in server-push mode that are registered to receive updates for an event.
    def push_update_for_event(self, clients, event_type):
        if len(clients)==0:
            return 0
        self.log_file.write("----PUSHING NEW EVENT UPDATE: %s----\n"%time.strftime("%d %b %Y %H:%M:%S", time.gmtime()))
        time_of_update = time.time() # Measure latency
        # Loop over all registered clients and send the update.
        for client_id in clients:
            client_ip, client_port = client_id
            s = xmlrpclib.ServerProxy("http://%s:%d"%(client_ip, client_port))
            # If a client has disconnected, unsubscribe that client from all teams and events.
            try:
                s.print_score_for_event(self.keeper.get_score(event_type), time_of_update)
                self.log_file.write("Successfully reached http://%s:%d\n"%(client_ip, client_port))
            except socket.error as err:
                self.log_file.write("Unable to reach http://%s:%d, unsubscribing.\n"%(client_ip, client_port))
                self.keeper.unregister_client(client_id)
        return 1

    # Updates clients in server-push mode that are registered to receive updates for a team.
    def push_update_for_team(self, clients, team_name):
        if len(clients)==0:
            return 0
        self.log_file.write("----PUSHING NEW EVENT UPDATE: %s----\n"%time.strftime("%d %b %Y %H:%M:%S", time.gmtime()))
        time_of_update = time.time() # Measure latency
        # Loop over all registered clients and send the update.
        for client_id in clients:
            client_ip, client_port = client_id
            s = xmlrpclib.ServerProxy("http://%s:%d"%(client_ip, client_port))
            # If a client has disconnected, unsubscribe that client from all teams and events.
            try:
                s.print_medal_tally_for_team(self.keeper.get_medal_tally(team_name), time_of_update)
                self.log_file.write("Successfully reached http://%s:%d\n"%(client_ip, client_port))
            except socket.error as err:
                self.log_file.write("Unable to reach http://%s:%d, unsubscribing.\n"%(client_ip, client_port))
                self.keeper.unregister_client(client_id)
        return 1

# Create the RPCHandler for ObelixServer.
class ObelixRPCHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

    # At one point, we got the client's IP address through this do_POST method, but now it is passed through the client_id.
    def do_POST(self):
        clientIP, clientPort = self.client_address
        print clientIP, clientPort
        SimpleXMLRPCRequestHandler.do_POST(self)

def main(ip, port=8000):
    log_file = open("log_server.txt", "w+", 5)
    server = AsyncXMLRPCServer((ip, port), requestHandler=ObelixRPCHandler) # Create the server
    server.register_introspection_functions()
    server.register_instance(ObelixServerFunctions(log_file)) # Register the RPC interface
    server.serve_forever() # Serve

if __name__ == "__main__":
    main(ip = HOST_NAME, port=8000)
