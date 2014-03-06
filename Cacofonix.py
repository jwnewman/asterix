import xmlrpclib
import numpy.random as rn
import time

from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler

s = xmlrpclib.ServerProxy('http://localhost:8000')

s.set_score("Stone Curling", "10")


# Print list of available methods
print s.system.listMethods()

TEAMS = ["Gaul", "Rome", "Carthage", "Greece", "Persia"]
MEDALS = ["gold", "silver", "bronze"]
EVENTS = ["Stone Curling", "Stone Skating", "Underwater Stone Weaving", "Synchronized Stone Swimming"]
UNITS = ["points", "laps", "baskets", "points"]

def create_flavor_statement(team, event, lead):
	# TODO: Make more variants
	return "What a day in %s! Currently in the lead is %s by %d %s."%(EVENTS[event].lower(), TEAMS[team], lead, UNITS[event])

class Cacofonix:
	def __init__(self, port, server_ip, server_port):
		self.port = port
		self.server = xmlrpclib.ServerProxy("%s:%d"%(server_ip, server_port))

	def set_score(self, event, score):
		# TODO get back ack/error
		self.server.set_score(event, score)

	def increment_medal_tally(self, team, medal):
		# TODO get back ack/error
		self.server.increment_medal_tally(team, medal)

def main(port=8001, server_ip, server_port):

	fonix = Cacofonix(port = port, server_ip = server_ip, server_port = server_port)

	while(True):
		rn.seed(10)

		time.sleep(rn.randint(5))
		event = rn.randint(len(EVENTS))
		team = rn.randint(len(TEAMS))
		lead = rn.randint(100)
		score = create_flavor_statement(team, event, lead)

		fonix.set_score(EVENTS[event], score)

		if rn.random() > 0.5:
			# choose three teams
			[gold, silver, bronze] = rn.choice(len(TEAMS), 3, replace=False)

			team = TEAMS[rn.randint(len(TEAMS))]
			medal = MEDALS[rn.randint(len(MEDALS))]

			[fonix.increment_medal_tally(TEAMS[team], MEDALS[medal]) for medal, team in enumerate(medal_winners)]














