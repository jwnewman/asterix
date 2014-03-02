class Event:

    def __init__(self, type):
        self.type = type
        self.score = ""
        print "Instantiated new Event with " + self.type

    def get_type(self):
        return self.type

    def set_score(self, score):
        self.score = score

    def get_score(self):
        return self.score
