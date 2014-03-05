class Event:

    def __init__(self, event_type):
        self.event_type = event_type
        self.score = ""
        print "Instantiated new Event with " + self.event_type

    def get_event_type(self):
        return self.event_type

    def set_score(self, score):
        self.score = score

    def get_score(self):
        return self.score
