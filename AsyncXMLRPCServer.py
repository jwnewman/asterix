from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from TimeServer import TimeServer
import threading
import socket
import SocketServer
import random

class AsyncXMLRPCServer(SocketServer.ThreadingMixIn,SimpleXMLRPCServer):
    def __init__(self, host, request_handler, hosts):
        self.uid = random.randint(0,100)
        self.offset = 0
        self.host = host
        self.time_server = TimeServer(hosts, self.uid, self.host)
        SimpleXMLRPCServer.__init__(self, host, request_handler)

    def get_host(self):
        return self.host

    def check_time_server(self):
        ack = self.time_server.check_time_server()
        threading.Timer(20, self.check_time_server).start()
        return ack

    def get_time_server_host(self):
        return self.time_server.get_leader_host()

    def elect_leader(self):
        return self.time_server.elect_leader()

    def get_id(self):
        return self.uid
