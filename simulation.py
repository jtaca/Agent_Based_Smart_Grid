import settings 
import map
from agents import charger_handler,driver_assistant,energy_broker,power_operative, geographic_agent
import random
import time
import threading
from PyQt5.QtCore import QEventLoop
from PyQt5.QtCore import QTimer


class simulation():

    def __init__(self):
        self.stop = 0
        self.steps = 100
        self.number_vehicles = 20
        self.number_priority_vehicles = random.choice(range(self.number_vehicles))
        self.number_stations = 2
        self.number_disasters = 0  #to generate the disaster pich an int between 0 and number of stepps
        self.step_of_disaster = []# we have to generate the impact of the disaster randomly
        self.standard_batery_size = 5000
        self.total_energy_of_tick = self.number_vehicles*self.standard_batery_size
        self.total_evergy_of_simulation = self.steps*self.total_energy_of_tick 
        tick_range = []
        if self.number_disasters>0:
            for i in range(self.steps):
                tick_range.append(i) 
            self.step_of_disaster = random.sample(tick_range, self.number_disasters)
            print(self.step_of_disaster)
        """ for i in range(self.number_disasters):
            c = random.choice(tick_range)
            tick_range.remove(c)
            print(tick_range)
            self.step_of_disaster.append(c) """
        print(self.number_priority_vehicles)
        self.step_time_sec = 1
        self.agent_list = []
        #storage available for PO
        self.storage_available = self.standard_batery_size*(self.number_vehicles/3) 
        self.energy_price_buy = 0.002
        self.energy_price_sell = 0.01

        #stats for simulation results
        self.profit_margin = [] #costof mantaining vs money made
        self.number_of_inactive_stations = []
        self.time_to_charge_worst_case =[]
        ##must add method calculate time to charge in DA
        self.number_comunications = []
        #has values per each tick/step
        

        pass

    def test(self,map1,gui):
        
        #c = geographic_agent.geographic_agent(38.7414116,-9.143627785022142)
        #print(b.get_latitude())
        
        gui.disp_vehicles.setText(str(self.number_vehicles))
        gui.disp_stations.setText(str(self.number_stations))
        gui.disp_priority.setText(str(self.number_priority_vehicles))

        listToStr = ' '.join([str(elem) for elem in self.step_of_disaster])
        gui.disp_outages.setText(str(self.number_disasters)+" in ticks: "+listToStr)

        lng, lat = map1.get_random_point()
        a = energy_broker.energy_broker(lat,lng,self.step_of_disaster,self.total_energy_of_tick, self.total_evergy_of_simulation)
        print(a.get_latitude())
        print(a.get_closest_node(map1.get_map()))

        lng, lat = map1.get_random_point()
        b = charger_handler.charger_handler(lat,lng, map1, self.energy_price_buy, self.energy_price_sell)

        #lng, lat = map1.get_random_point()
        #c = geographic_agent.geographic_agent(lat,lng)
        #c = driver_assistant.driver_assistant(lat,lng, self.standard_batery_size)

        lng, lat = map1.get_random_point()
        #c = geographic_agent.geographic_agent(lat,lng)
        
        d = power_operative.power_operative(lat,lng, self.storage_available)


        agent_list = []
        agent_list.append(a)
        agent_list.append(b)
        #agent_list.append(c)
        agent_list.append(d)

        map1.add_agents(agent_list)

        self.curret_step = 0
        
        def worker():
            #last_step = 0
            #while self.curret_step < self.steps: 
                #if last_step < self.curret_step: 
            print(self.curret_step)
            gui.disp_time.setText(str(self.curret_step))
            gui.reload_map()
            
        #thread = threading.Thread(target=worker)
        #thread.start()
        for curret_step in range(self.steps):

            lng, lat = map1.get_random_node()
            agent_list.append(driver_assistant.driver_assistant(lat,lng, self.standard_batery_size))
            map1.add_agents(agent_list)










            loop = QEventLoop()
            QTimer.singleShot(self.step_time_sec, loop.quit)
            loop.exec_()
            self.curret_step = curret_step
            #print(self.curret_step)
            gui.disp_time.setText(str(self.curret_step))
            gui.reload_map()
            
        gui.disp_time.setText("Complete")
            
    
    def One_DA_N_CH(N):
        pass

    def update(self, gui):
        loop = QEventLoop()
        QTimer.singleShot(self.step_time_sec, loop.quit)
        loop.exec_()
        self.curret_step = curret_step
        print(self.curret_step)
        gui.disp_time.setText(str(self.curret_step))
        gui.reload_map()

    def N_DA_N_CH(self,map1,gui):

        gui.disp_vehicles.setText(str(self.number_vehicles))
        gui.disp_stations.setText(str(self.number_stations))
        gui.disp_priority.setText(str(self.number_priority_vehicles))
        listToStr = ' '.join([str(elem) for elem in self.step_of_disaster])
        gui.disp_outages.setText(str(self.number_disasters)+" in ticks: "+listToStr)
        self.agent_list = []
        aux_priori = self.number_priority_vehicles
        for i in range(self.number_vehicles):
            lng, lat = map1.get_random_point()
            rand_bat = random.uniform(self.standard_batery_size* 0.6, self.standard_batery_size)
            if (aux_priori>0):
                aux_priori-= 1
                c = driver_assistant.driver_assistant(lat,lng, rand_bat)
                # this has to have priority
            
            c = driver_assistant.driver_assistant(lat,lng, rand_bat)
            self.agent_list.append(c)

        for i in range(self.number_stations):
            lng, lat = map1.get_random_point()
            c = charger_handler.charger_handler(lat,lng, map1)
            self.agent_list.append(c)

        lng, lat = map1.get_random_point()
        eb = energy_broker.energy_broker(lat,lng)
        lng, lat = map1.get_random_point()
        po = power_operative.power_operative(lat,lng)
        self.agent_list.append(eb)
        self.agent_list.append(po)
       
        map1.add_agents(self.agent_list)
        self.curret_step = 0
        
        for curret_step in range(self.steps):

            for agent in self.agent_list:
                agent.act()










            update(gui)
            
        gui.disp_time.setText("Complete")

    def One_DA_One_CH(N):
        pass

    def N_DA_One_CH(N):
        pass

    def stop(self):
        if self.stop == 0:
            self.stop = 1
        else:
            self.stop = 0
        

