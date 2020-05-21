import agents.geographic_agent


class energy_broker(agents.geographic_agent.geographic_agent):

    def __init__(self,lat,lng, step_of_disaster, total_energy_of_tick, total_evergy_of_simulation ):
        agents.geographic_agent.geographic_agent.__init__(self,lat,lng)
        self.name = "energy broker"
        self.step_of_disaster = step_of_disaster
        self.total_energy_of_tick = total_energy_of_tick
        self.total_evergy_of_simulation = total_evergy_of_simulation 

    def act(self):
        pass # check if its time of accident or not and acct accordingly

    def do_power_outage(self):
        pass
    
    def do_power_redistribution(self): 
        pass

    def concede_energy_to_po(self):
        pass

    
    

