#!/usr/bin/env python
"""Module for DBServer and related classes."""

import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
import threading
import socket
import time
import getopt
import os
import sys
from DatabaseManager import DatabaseManager
from AsyncXMLRPCServer import AsyncXMLRPCServer
from ServerFunctions import ServerFunctions

class DBServerFunctions(ServerFunctions):
    """Implements functions for the DBServer.

    Arguments:
    server -- The active server object implementing these methods.
    """
    def __init__(self, server):
        self.db_mgr = DatabaseManager()
        ServerFunctions.__init__(self, server)

    def set_score(self, event_type, score, timestamp):
        """Sets the score for a given event via RPC to the DB Manager.

        Always called by ScoreKeeper.

        Arguments:
        event_type -- String for one of the Olympic events.
        score -- String for the updated score.
        timestamp -- Time of the update.
        """
        return self.db_mgr.set_score(event_type, score, timestamp)

    def get_score(self, event_type, client_id, vector_clock_str):
        """Returns synced vector clock and current score for a given event via RPC to the DB Manager.

        Always called by ScoreKeeper.

        First syncs vector clock with the vector clock passed in.

        Arguments:
        event_type -- String for one of the Olympic events.
        client_id -- Unique string ID of the initial requesting client (used for raffle).
        vector_clock_str -- String representation of the vector clock of the frontend server.
        """
        synched_clock_str = self.server.sync_with_vector_clock(vector_clock_str)
        self.db_mgr.check_raffle(client_id, synched_clock_str)
        return synched_clock_str, self.db_mgr.get_score(event_type)

    def increment_medal_tally(self, team_name, medal_type, timestamp):
        """Increments the medal tally for a given team via RPC to the DB Manager.

        Always called by ScoreKeeper.

        Arguments:
        team_name -- String for one of the Olympic teams.
        medal_type -- String for the type of medal to increment.
        timestamp -- Time of the update.
        """
        return self.db_mgr.increment_medal_tally(team_name, medal_type, timestamp)

    def get_medal_tally(self, team_name, client_id, vector_clock_str):
        """Returns synced vector clock and current medal tally for a given team via RPC to the DB Manager.

        Always called by ScoreKeeper.

        First syncs vector clock with the vector clock passed in.

        Arguments:
        team_name -- String for one of the Olympic teams.
        client_id -- Unique string ID of the initial requesting client (used for raffle).
        vector_clock_str -- String representation of the vector clock of the frontend server.
        """
        synched_clock_str = self.server.sync_with_vector_clock(vector_clock_str)
        self.db_mgr.check_raffle(client_id, synched_clock_str)
        return synched_clock_str, self.db_mgr.get_medal_tally(team_name)
    
class DatabaseRPCHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

    def do_POST(self):
        clientIP, clientPort = self.client_address
        print clientIP, clientPort
        SimpleXMLRPCRequestHandler.do_POST(self)

def main(ip, port=8000, uid=0, frontends=[('localhost', 8002), ('localhost', 8003)]):
    hosts = [(ip, port)] + frontends
    server = AsyncXMLRPCServer(uid, DatabaseRPCHandler, hosts)
    server.register_introspection_functions()
    server.register_instance(DBServerFunctions(server))
    t = threading.Timer(10, server.check_time_server)
    t.daemon = True
    t.start()
    server.serve_forever()

if __name__ == "__main__":
    local = True
    try:
        opts, args = getopt.getopt(sys.argv[1:], "lp:i:x:y:", ["run_locally","port=","uid=","xhost=","yhost="])

    except getopt.error, msg:
        print msg
        sys.exit(2)
    for o, a in opts:
        if o in ("-h", "--help"):
            print __doc__
            sys.exit(0)
        elif o in ("-l", "--run_locally"):
            local = True
        elif o in ("-p", "--port"):
            port = int(a)
        elif o in ("-i", "--uid"):
            uid = int(a)
        elif o in ("-x", "--xhost"):
            xip, xport = a.split(":")
            xport = int(xport)
        elif o in ("-y", "--yhost"):
            yip, yport = a.split(":")
            yport = int(yport)
    port = 8000
    uid = 0
    if local:
        ip = "localhost"
        xip = "localhost"
        xport = 8002
        yip = "localhost"
        yport = 8003
    else:
        ip = socket.gethostbyname(socket.gethostname())
    main(ip=ip, port=port, uid=uid, frontends =[(xip, xport), (yip, yport)])

