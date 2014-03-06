import xmlrpclib
import socket
import time
from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler

uid = 8001

class ListenerFunctions:
    def print_medal_tally_for_team(self, medal_tally):
        print medal_tally
        
    def print_score_for_event(self, score):
        print score

class TabletRPCHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)


# Create server
callback_server = SimpleXMLRPCServer(("localhost", uid),
                            requestHandler=TabletRPCHandler)
callback_server.register_introspection_functions()

callback_server.register_instance(ListenerFunctions())

s = xmlrpclib.ServerProxy('http://localhost:8000')

print s.register_client(uid, "Stone Curling")
    

callback_server.serve_forever()

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



def main(port, server_ip, server_port, teams = [], events = [], client_pull = True, pull_rate = 10):
	client = StoneTablet(port, server_ip, server_port, teams, events)

	# Client-pull architecture
	while(client_pull):
		client.pull()
		time.sleep(pull_rate)

	# Server-push architecture
	client.serve()



		







