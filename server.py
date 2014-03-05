
class ObelixServer:

	def __init__(self):
		__scores = {}
		__users = []

	def get_medal_tally(self, team_name):
		"""Returns the number of gold, silver and bronze leafs earned by the team_name. 
		Your system should track medal tallies for at least two teams, namely Gaul and Rome.
		"""
		raise NotImplementedError
q
	def increment_medal_tally(self, team_name, medal_type):
		"""Increments the medal tally for the specified team, and medal_type. 
		Can be bronze, silver, or gold and the appropriate medal count for that team is incremented.
		"""
		raise NotImplementedError


getScore(eventType), which provides the latest score for the specified eventType. Pick at least three winter Olympics events such as stone Curling and stone skating and provide scores for these events.
setScore(eventType), which updates the current score for the specified event.

