class Team:

    def __init__(self, name):
        self.name = name
        self.gold_medals = 0
        self.silver_medals = 0
        self.bronze_medals = 0
        self.clients = []
        print "Instantiated new team : " + self.name

    def get_team_name(self):
        return self.name

    # def get_medal_tally(self):
    #     return (self.gold_medals, self.silver_medals, self.bronze_medals)

    # def to_string(self):
    #     # return "Team " + self.name + " has :\n" + str(self.gold_medals) + " gold medals \n" + str(self.silver_medals) + " silver medals \n" + str(self.bronze_medals) + " bronze medals\n"
    #     return "Team %s has:\n%d gold medals\n%d silver medals\n\%d bronze medals\n"%(self.name, self.gold_medals, self.silver_medals, self.bronze_medals)

    def get_medal_tally(self):
        return "Team %s has:\n%d gold medals\n%d silver medals\n%d bronze medals\n"%(self.name, self.gold_medals, self.silver_medals, self.bronze_medals)


    def increment_medals(self, medal_type):
        self.__dict__["%s_medals"%medal_type] += 1

    # def get_gold_medals(self):
    #     return self.gold_medals

    # def get_silver_medals(self):
    #     return self.silver_medals

    # def get_bronze_medals(self):
    #     return self.bronze_medals

    def increment_gold_medals(self):
        self.gold_medals += 1

    def increment_silver_medals(self):
        self.silver_medals += 1

    def increment_bronze_medals(self):
        self.bronze_medals += 1


    def add_client(self, client_id):
        self.clients.append(client_id)

    def get_clients(self):
        return self.clients
