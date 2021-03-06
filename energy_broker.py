import geographic_agent
import random


class energy_broker(geographic_agent.geographic_agent):

    def __init__(self,lat,lng, step_of_disaster, total_energy_of_tick, total_evergy_of_simulation , simulation, step_of_redistribuition, min_flactuation, max_flactuation):
        geographic_agent.geographic_agent.__init__(self,lat,lng,'y', 's', 200,2)
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
        for i in self.simulation.agent_list:
            if i.name == "power operative":
                self.power_operative = i

    def act(self):
        self.energy_available = self.total_energy_of_tick
        aux_is_outage = False

        if self.simulation.current_step in self.step_of_redistribuition and  not aux_is_outage:
            self.simulation.map1.add_points_to_print((self.get_longitude(),self.get_latitude()),'r','2',100)
            self.do_power_redistribution()

            self.step_of_redistribuition.remove(self.simulation.current_step)
            
        if len(self.step_of_disaster) > 0 and self.simulation.current_step in self.step_of_disaster:
            self.do_power_outage()
            self.simulation.map1.add_points_to_print((self.get_longitude(),self.get_latitude()),'k','2',100)
            aux_is_outage = True


            self.step_of_disaster.remove(self.simulation.current_step)
            
            
        
            
        self.concede_energy_to_po()

        
            
        self.energy_history.append(self.energy_available)
           
        
        pass # check if its time of accident or not and acct accordingly

    def do_power_outage(self):
        print("EB: outage")
        self.energy_available = 0
        pass
    
    def do_power_redistribution(self): 
        print("EB: redistribution")
        self.energy_available =  random.uniform(self.flactuation_min, self.flactuation_max) # """self.total_energy_of_tick -""" 
        pass

    def concede_energy_to_po(self):
        print("EB: I give to PO  "+ str( self.energy_available))
        self.power_operative.recieve_energy(self.energy_available)
        pass

    
    

