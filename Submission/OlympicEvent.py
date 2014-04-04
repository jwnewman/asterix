# This class contains all the information that an OlympicEvent needs to store about itself and provides getters and setters.
# Namely, this information is the name of the event, the current score, and the contact information for any clients registered
# for this event in server push mode.

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
        
