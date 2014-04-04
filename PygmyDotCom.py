#!/usr/bin/env python
"""Module for all of the classes involved in implementing Pygmy.com.

The main class is PygmyServerFunctions which implements PygmyServer's functionality.
PygmyServer is just another AsyncXMLRPCServer.
"""
import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from AsyncXMLRPCServer import AsyncXMLRPCServer
from ServerFunctions import ServerFunctions
from threading import Lock
from ScoreKeeper import ScoreKeeper
from Global import Global
import socket
import SocketServer
import time
import getopt
import os
import sys
import random
import types
from Synchronized import synchronized, synchronized_check

COUNTER_LOCK = Lock()

class PygmyServerFunctions:
	"""PygmyServer is the middleman between clients and the two frontend servers.

	It implements a simple load-balancing scheme to spread requests between the frontends.

	Arguments:
	db -- (ip, host) tuple which is the address of the database server.
	frontends -- list of (ip, host) tuples which are the addresses of the frontends. 
	"""
	def __init__(self, db, frontends):
		self.db = db
		self.frontends = frontends
		self.event_count = 0 # strictly for testing

	@synchronized(COUNTER_LOCK)
	def increment_counter(self):
		"""Strictly for testing purposes."""
		self.event_count += 1

	def get_active_servers(self):
		"""Returns a list of connections to available frontend servers.

		If no servers are available, an empty list is returned.
		"""
		servers = []
		for ip, port in self.frontends:
			try:
				s = xmlrpclib.ServerProxy("http://%s:%d"%(ip, port))
				servers.append(s)
			except socket.error:
				pass
		return servers

	def load_balance(self):
		"""Simple load-balancing scheme:
		Returns an available server uniformly at random.

		If no servers are available, returns None.
		"""
		servers = self.get_active_servers()
		return random.choice(servers) if servers else None

	def get_medal_tally(self, team_name, client_id):
		"""Returns the current medal tally for a given team via RPC to one of the frontend servers.

		Calls load_balance to get one of the available frontends randomly.

		Always called by a requesting client.

		Arguments:
		team_name -- String for one of the Olympic teams.
		client_id -- Unique string ID of the requesting client (used for raffle).
		"""
		self.increment_counter()
		server = self.load_balance()
		if type(server) is not types.NoneType:
			return server.get_medal_tally(team_name, client_id)
		else:
			return "Error 1928391 -- Sorry I'm not sorry"

	def increment_medal_tally(self, team_name, medal_type, password):
        """Increments the medal tally for a given team via RPC to one of the frontend servers.

        Calls load_balance to get one of the available frontends randomly.

        Always called by Cacofonix.

        Arguments:
        team_name -- String for one of the Olympic teams.
        medal_type -- String for the type of medal to increment.
        password -- Unique password only known by Cacofonix (hopefully).
        """
		server = self.load_balance()
		if type(server) is not types.NoneType:
			return server.increment_medal_tally(team_name, medal_type, password)
		else:
			return "Error 1928391 -- Sorry I'm not sorry"

	def get_score(self, event_type, client_id):
		"""Returns the current score for a given event via RPC to one of the frontend servers.

		Calls load_balance to get one of the available frontends randomly.

		Always called by a requesting client.

		Arguments:
		event_type -- String for one of the Olympic events.
		client_id -- Unique string ID of the requesting client (used for raffle).
		"""
		self.increment_counter()
		server = self.load_balance()
		if type(server) is not types.NoneType:
			return server.get_score(event_type, client_id)
		else:
			return "Error 1928391 -- Sorry I'm not sorry"

	def set_score(self, event_type, score, password):
        """Sets the score for a given event via RPC to one of the frontend servers.

        Calls load_balance to get one of the available frontends randomly.

        Always called by Cacofonix.

        Arguments:
        event_type -- String for one of the Olympic events.
        score -- String for the updated score.
        password -- Unique password only known by Cacofonix (hopefully).
        """
		server = self.load_balance()
		if type(server) is not types.NoneType:
			server.set_score(event_type, score, password)
		else:
			return "Error 1928391 -- Sorry I'm not sorry"

class PygmyServer(SocketServer.ThreadingMixIn, SimpleXMLRPCServer): pass

class PygmyRPCHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

    def do_POST(self):
        clientIP, clientPort = self.client_address
        print clientIP, clientPort
        SimpleXMLRPCRequestHandler.do_POST(self)

def main(ip, port=8001):
	db = ('localhost', 8000)
	frontends = [('localhost', 8002), ('localhost', 8003)]

	server = PygmyServer((ip, port), PygmyRPCHandler)
	server.register_introspection_functions()
	server.register_instance(PygmyServerFunctions(db, frontends))
	server.serve_forever()

if __name__ == "__main__":
	main('localhost', 8001)
