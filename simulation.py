import settings 
import map
from agents import charger_handler,driver_assistant,energy_broker,power_operative, geographic_agent


class simulation(agents.geographic_agent.geographic_agent):

    def __init__():
        pass

    def test():
        map1 = map.map()
        b = geographic_agent.geographic_agent(38.7414116,-9.143627785022142)
        print(b.get_latitude())
        a = energy_broker.energy_broker(38.7414116,-9.143627785022142)
        print(a.get_latitude())

        print(a.get_closest_node(map1.get_map()))
    
    def One_DA_N_CH(N):
        pass

    def N_DA_N_CH(N):
        pass

    def One_DA_One_CH(N):
        pass

    def N_DA_One_CH(N):
        pass