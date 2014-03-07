class OlympicEvent:
    def __init__(self, event_type):
        self.event_type = event_type
        self.score = ""
        self.clients = []
        print "Instantiated new Event with " + self.event_type

    def get_event_type(self):
        return self.event_type

    def set_score(self, score):
        self.score = score

    def get_score(self):
        return self.score

    def add_client(self, client_id):
        self.clients.append(client_id)

    def remove_client(self, client_id):
        self.clients.remove(client_id)

    def get_clients(self):
        return self.clients
        
