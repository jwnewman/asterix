#!/usr/bin/env python

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
import numpy as np
import random
import types
from Synchronized import synchronized, synchronized_check

COUNTER_LOCK = Lock()

# def synchronized(lock):
#     def wrap(f):
#         def newFunction(*args, **kw):
#             lock.acquire()
#             try:
#                 return f(*args, **kw)
#             finally:
#                 lock.release()
#         return newFunction
#     return wrap

class PygmyServer(SocketServer.ThreadingMixIn, SimpleXMLRPCServer): pass

class PygmyRPCHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

    def do_POST(self):
        clientIP, clientPort = self.client_address
        print clientIP, clientPort
        SimpleXMLRPCRequestHandler.do_POST(self)

class PygmyServerFunctions:
	def __init__(self, db, frontends):
		self.db = db # tuple of (ip, host)
		self.frontends = frontends # list of tuples of (ip, host)
		self.event_count = 0 # strictly for testing

	@synchronized(COUNTER_LOCK)
	def increment_counter(self):
		"""Strictly for testing purposes."""
		self.event_count += 1

	def get_active_servers(self):
		servers = []
		for ip, port in self.frontends:
			try:
				s = xmlrpclib.ServerProxy("http://%s:%d"%(ip, port))
				servers.append(s)
			except socket.error:
				pass
		return servers

	def load_balance(self):
		servers = self.get_active_servers()
		return random.choice(servers) if servers else None

	def get_medal_tally(self, team_name, client_id):
		self.increment_counter()
		server = self.load_balance()
		if type(server) is not types.NoneType:
			return server.get_medal_tally(team_name, client_id)
		else:
			return "Error 1928391 -- Sorry I'm not sorry"

	def increment_medal_tally(self, team_name, medal_type, password):
		server = self.load_balance()
		if type(server) is not types.NoneType:
			return server.increment_medal_tally(team_name, medal_type, password)
		else:
			return "Error 1928391 -- Sorry I'm not sorry"

	def get_score(self, event_type, client_id):
		self.increment_counter()
		server = self.load_balance()
		if type(server) is not types.NoneType:
			return server.get_score(event_type, client_id)
		else:
			return "Error 1928391 -- Sorry I'm not sorry"

	def set_score(self, event_type, score, password):
		server = self.load_balance()
		if type(server) is not types.NoneType:
			server.set_score(event_type, score, password)
		else:
			return "Error 1928391 -- Sorry I'm not sorry"

def main(ip, port=8001):
	db = ('localhost', 8000)
	frontends = [('localhost', 8002), ('localhost', 8003)]

	server = PygmyServer((ip, port), PygmyRPCHandler)
	server.register_introspection_functions()
	server.register_instance(PygmyServerFunctions(db, frontends))
	server.serve_forever()

if __name__ == "__main__":
	main('localhost', 8001)
