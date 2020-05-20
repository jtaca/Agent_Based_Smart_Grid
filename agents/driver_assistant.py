import agents.geographic_agent


class driver_assistant(agents.geographic_agent.geographic_agent):

        def __init__(self,lat,lng):
            agents.geographic_agent.geographic_agent.__init__(self,lat,lng)
            self.name = "driver assistant"