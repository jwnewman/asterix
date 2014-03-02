class Team:

    def __init__(self, name):
        self.name = name
        self.gold_medals = 0
        self.silver_medals = 0
        self.bronze_medals = 0
        print "Instantiated new team : " + self.name

    def get_team_name(self):
        return self.name

    def get_medal_tally(self):
        return "Team " + self.name + " has :\n" + str(self.gold_medals) + " gold medals \n" + str(self.silver_medals) + " silver medals \n" + str(self.bronze_medals) + " bronze medals\n"

    def get_gold_medals(self):
        return self.gold_medals

    def get_silver_medals(self):
        return self.silver_medals

    def get_bronze_medals(self):
        return self.bronze_medals

    def increment_gold_medals(self):
        self.gold_medals = self.gold_medals+1

    def increment_silver_medals(self):
        self.silver_medals = self.silver_medals+1

    def increment_bronze_medals(self):
        self.bronze_medals = self.bronze_medals+1
