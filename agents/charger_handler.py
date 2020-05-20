import agents.geographic_agent


class charger_handler(agents.geographic_agent.geographic_agent):

	def __init__(self,lat,lng, G):
		agents.geographic_agent.geographic_agent.__init__(self,lat,lng)
		self.name = "charger handler"
		self.grid = G

