import settings 
import map
import charger_handler,driver_assistant,energy_broker,power_operative, geographic_agent
import random
import time
import threading
import numpy as np
import networkx as nx
import settings
from PyQt5.QtCore import QEventLoop
from PyQt5.QtCore import QTimer


class simulation():

    def __init__(self):
        self.stop = 0
        self.steps = 10
        self.number_vehicles = 20
        self.number_priority_vehicles = random.choice(range(self.number_vehicles)) #7
        self.number_stations = 2
        self.number_disasters = 3  #to generate the disaster pick an int between 0 and number of stepps
        self.step_of_disaster = []# we have to generate the impact of the disaster randomly
        self.number_redistribuition = 7  #to generate the redistribuition pick an int between 0 and number of stepps
        self.step_of_redistribuition = []# we have to generate the impact of the redistribuition randomly
        self.max_flactuation = 1 # if we put min and max equal the flactuation is the same every time
        self.min_flactuation = 0.6
        self.standard_batery_size = 5000 # this can flactuate per car
        self.total_energy_of_tick = self.number_vehicles*self.standard_batery_size
        self.total_evergy_of_simulation = self.steps*self.total_energy_of_tick 
        tick_range = []
        if self.number_disasters>0 or self.number_redistribuition>0:
            for i in range(self.steps):
                tick_range.append(i) 
            self.step_of_disaster = random.sample(tick_range, self.number_disasters)
            print(self.step_of_disaster)

            for i in range(self.steps):
                tick_range.append(i) 
            self.step_of_redistribuition = random.sample(tick_range, self.number_redistribuition)
            print(self.step_of_redistribuition)
        print(self.number_priority_vehicles)
        self.step_time_sec = 1
        self.agent_list = []
        #storage available for PO
        self.storage_available = self.standard_batery_size*(self.number_vehicles/3) 
        self.energy_price_buy = 0.002
        self.energy_price_sell = 0.01
        self.current_step = 0
        self.architecture = "Not yet chosen"

        #stats for simulation results
        self.profit_margin = [] #costof mantaining vs money made
        self.number_of_inactive_stations = []
        self.time_to_charge_worst_case =[]
        ##must add method calculate time to charge in DA
        self.number_comunications = []
        #has values per each tick/step
        self.energy_history = []
    

        

        pass


    def update(self,current_step, gui):
        loop = QEventLoop()
        QTimer.singleShot(self.step_time_sec, loop.quit)
        loop.exec_()
        self.current_step = current_step
        print(self.current_step)
        gui.disp_time.setText(str(self.current_step))
        gui.reload_map()

    def end(self, gui):
        gui.disp_time.setText("Complete")
        print("Complete")

    def graph(self,agent_list):
        for agent in agent_list:
            if agent.name == "energy broker":
                self.energy_history = agent.energy_history
                break
            else:
                self.energy_history = "energy_history not found"

        print(self.energy_history)
        #graph this series 
        #https://matplotlib.org/2.1.1/api/_as_gen/matplotlib.pyplot.plot.html
        

    def test(self,map1,gui):
        self.architecture = "Test"
        #c = geographic_agent.geographic_agent(38.7414116,-9.143627785022142)
        #print(b.get_latitude())
        
        gui.disp_vehicles.setText(str(self.number_vehicles))
        gui.disp_stations.setText(str(self.number_stations))
        gui.disp_priority.setText(str(self.number_priority_vehicles))
        map1.clean_map()

        listToStr = ' '.join([str(elem) for elem in self.step_of_disaster])
        gui.disp_outages.setText(str(self.number_disasters)+" in ticks: "+listToStr)

        lng, lat = map1.get_random_point()
        a = energy_broker.energy_broker(lat,lng,self.step_of_disaster,self.total_energy_of_tick, self.total_evergy_of_simulation, self,  self.step_of_redistribuition, self.max_flactuation, self.min_flactuation)
        #print(a.get_latitude())
        #print(a.get_closest_node(map1.get_map()))

        lng, lat = map1.get_random_point()
        b = charger_handler.charger_handler(lat,lng, map1, self.energy_price_buy, self.energy_price_sell)

        #DRIVER ASSISTANT
        #Generate a route -> TODO: Have a function that do this
        route = []
        no_route = True
        A = None
        while no_route:
            try:
                # A->B
                A = np.random.choice(map1.G.nodes)
                B = np.random.choice(map1.G.nodes)
                r = nx.shortest_path(map1.G, A, B, weight='length')
                route.append(r)

                # B->C
                C = np.random.choice(map1.G.nodes)
                r = nx.shortest_path(map1.G, B, C, weight='length')
                route.append(r)

                # C->A
                r = nx.shortest_path(map1.G, C, A, weight='length')
                route.append(r)

                no_route = False
            except:
                print("Route couldn't be created.... Retrying")
        
        is_priority = True
        c = driver_assistant.driver_assistant(A, route, self.standard_batery_size , map1, is_priority)
        
        #lng, lat = map1.get_random_point()
        #c = geographic_agent.geographic_agent(lat,lng)
        #c = driver_assistant.driver_assistant(lat,lng, self.standard_batery_size)
        #c = geographic_agent.geographic_agent(lat,lng)

        
        lng, lat = map1.get_random_point()
        d = power_operative.power_operative(lat,lng, self.storage_available)


        agent_list = []
        agent_list.append(a)
        agent_list.append(b)
        agent_list.append(c)
        agent_list.append(d)

        map1.add_agents(agent_list)

        self.current_step = 0
        
        def worker():
            #last_step = 0
            #while self.curret_step < self.steps: 
                #if last_step < self.curret_step: 
            print(self.curret_step)
            gui.disp_time.setText(str(self.curret_step))
            gui.reload_map()
            
        #thread = threading.Thread(target=worker)
        #thread.start()
        for current_step in range(self.steps):

            #lng, lat = map1.get_random_node()
            #agent_list.append(driver_assistant.driver_assistant(lat,lng, self.standard_batery_size))
            #map1.add_agents(agent_list)

            a.act()







            self.update(current_step,gui)
            #loop = QEventLoop()
            #QTimer.singleShot(self.step_time_sec, loop.quit)
            #loop.exec_()
            #self.curret_step = curret_step
            #print(self.curret_step)
            #gui.disp_time.setText(str(self.curret_step))
            #gui.reload_map()
        self.end(gui)  
        self.graph(agent_list)
        
            
    
    def One_DA_N_CH(self,N):
        self.architecture = "1 DA; N CH; 1 PO; 1 EB"
        pass

    def N_DA_N_CH(self,map1,gui):
        self.architecture = "N DA; N CH; 1 PO; 1 EB"

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










            update(current_step,gui)
            
        gui.disp_time.setText("Complete")

    def One_DA_One_CH(self, N):
        self.architecture = "1 DA; 1 CH; 1 PO; 1 EB"
        pass

    def N_DA_One_CH(self,N):
        self.architecture = "N DA; 1 CH; 1 PO; 1 EB"
        pass

    def stop(self):
        if self.stop == 0:
            self.stop = 1
        else:
            self.stop = 0
        

