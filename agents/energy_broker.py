import agents.geographic_agent
import random


class energy_broker(agents.geographic_agent.geographic_agent):

    def __init__(self,lat,lng, step_of_disaster, total_energy_of_tick, total_evergy_of_simulation , simulation, step_of_redistribuition, min_flactuation, max_flactuation):
        agents.geographic_agent.geographic_agent.__init__(self,lat,lng)
        self.name = "energy broker"
        self.step_of_disaster = step_of_disaster
        self.step_of_redistribuition = step_of_redistribuition
        self.total_energy_of_tick = total_energy_of_tick # if simulation time is fast add an etra random here to simulate little flatuations in power
        self.energy_available = 0
        self.total_evergy_of_simulation = total_evergy_of_simulation 
        self.simulation = simulation
        self.flactuation_min = self.total_energy_of_tick*min_flactuation
        self.flactuation_max = self.total_energy_of_tick*max_flactuation
        self.energy_history = []

    def act(self):
        self.energy_available = self.total_energy_of_tick
        aux_is_outage = False
        if self.simulation.current_step in self.step_of_disaster:
            self.do_power_outage()
            aux_is_outage = True
        if self.simulation.current_step in self.step_of_redistribuition and  not aux_is_outage:
            self.do_power_redistribution()

        self.concede_energy_to_po()
           
        
        pass # check if its time of accident or not and acct accordingly

    def do_power_outage(self):
        print("outage")
        self.energy_available = 0
        self.flactuation_min = 0
        self.flactuation_max = 0
        pass
    
    def do_power_redistribution(self): 
        print("redistribution")
        self.energy_available =   self.total_energy_of_tick - random.uniform(self.flactuation_min, self.flactuation_max)
        pass

    def concede_energy_to_po(self):
        self.energy_history.append(self.energy_available)
        print("eb give: "+ str( self.energy_available))
        pass

    
    

