import xmlrpclib
import socket
import time
from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
import numpy.random as rn

TEAMS = ["Gaul", "Rome", "Carthage", "Greece", "Persia"]
EVENTS = ["Stone Curling", "Stone Skating", "Underwater Stone Weaving", "Synchronized Stone Swimming"]

class StoneTablet:
	def __init__(self, port, server_ip, server_port, teams=[], events=[]):
		self.port = port
		self.teams = teams
		self.events = events
		self.server = xmlrpclib.ServerProxy("%s:%d"%(server_ip, server_port))

	# Methods for client-pull architecture

	def get_medal_tally(self, team):
		return self.server.get_medal_tally(team)

	def get_score(self, event):
		return self.server.get_score(event)

	def pull(self):
		for team in self.teams:
			print self.get_medal_tally(team)
		for event in self.events:
			print self.get_score(event)

	# Methods for server-push architecture

	class ListenerFunctions:
		def print_medal_tally_for_team(self, medal_tally):
			print medal_tally
		def print_score_for_event(self, score):
			print score

	def get_my_IP(self):
		# TODO
		return '127.0.0.1'

	def register_with_server(self):
		print self.server.register_client(port = self.port, events = self.events, teams = self.teams)

	def serve(self):
		callback_server = SimpleXMLRPCServer("%s:%d"%(self.get_my_IP(), self.port))
		callback_server.register_introspection_functions()
		self.register_with_server()
		callback_server.serve_forever()

def main(port, teams = ["Gaul"], events = ["Stone Curling"], server_ip='http://localhost', server_port=8000, client_pull = True, pull_rate = 10):
	client = StoneTablet(port, server_ip, server_port, teams, events)

	# Client-pull architecture
	while(client_pull):
		client.pull()
		time.sleep(pull_rate)

	# Server-push architecture
	client.serve()

if __name__ == "__main__":
	port = rn.randint(8002, 9000)
	num_teams = rn.randint(1, len(TEAMS)+1)
	num_events = rn.randint(1, len(EVENTS)+1)
	print rn.choice(len(TEAMS), num_teams, replace=False)
	fav_teams = [TEAMS[t] for t in rn.choice(len(TEAMS), num_teams, replace=False)]
	fav_events = [EVENTS[e] for e in rn.choice(len(EVENTS), num_events, replace=False)]

	main(port=port, teams=fav_teams, events=fav_events)




		







