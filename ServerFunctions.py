import datetime
from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler

class ServerFunctions():

    def __init__(self, server):
        self.server = server    

    def get_time_in_seconds(self):
        time = datetime.datetime.now().time()
        return (time.hour * 3600) + (time.minute * 60) + time.second

    def get_host(self):
        return self.server.host

    def get_id(self):
        return self.server.get_id()

    def get_leader(self):
        return self.server.get_time_server_host()

    def elect_leader(self):
        return self.server.elect_leader()

    def set_offset(self, offset):
        self.server.set_offset(offset)
        print "New offset is " + str(self.server.offset)
        print "Testing timestamp:"
        self.get_timestamp()
        return True

    def get_timestamp(self):
        time = datetime.datetime.now().time()
        fulldate = datetime.datetime(100, 1, 1, time.hour, time.minute, time.second)
        date = fulldate + datetime.timedelta(days=0,seconds=self.server.get_offset())
        time = date.time()
        timestamp = time.strftime('%H:%M:%S')
        print timestamp
        return timestamp
