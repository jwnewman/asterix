import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler

s = xmlrpclib.ServerProxy('http://localhost:8000')

s.set_score("Stone Curling", "10")


# Print list of available methods
print s.system.listMethods()
