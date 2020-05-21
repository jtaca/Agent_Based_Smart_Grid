import agents.geographic_agent


class charger_handler(agents.geographic_agent.geographic_agent):

	def __init__(self,lat,lng, map):
		agents.geographic_agent.geographic_agent.__init__(self,lat,lng)
		self.name = "charger handler"
		self.map = map


