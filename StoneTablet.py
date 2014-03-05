import xmlrpclib
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
