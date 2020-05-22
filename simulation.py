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
from matplotlib import pyplot as plt
import statistics


class simulation():

    def __init__(self):
        self.stop_tog = False
        self.steps = settings.simulation_time
        self.number_vehicles = settings.nr_vehicles
        self.number_priority_vehicles = settings.nr_priority_vehicles #random.choice(range(self.number_vehicles)) #7
        self.number_stations = settings.nr_stations
        self.number_disasters = settings.nr_disasters  #to generate the disaster pick an int between 0 and number of stepps
        self.step_of_disaster = []# we have to generate the impact of the disaster randomly
        self.number_redistribuition = settings.nr_redistribution  #to generate the redistribuition pick an int between 0 and number of stepps
        self.step_of_redistribuition = []# we have to generate the impact of the redistribuition randomly
        self.max_flactuation = settings.max_source_flactuation # if we put min and max equal the flactuation is the same every time
        self.min_flactuation = settings.min_source_flactuation
        self.standard_batery_size = settings.standard_batery_size # this can flactuate per car
        self.total_energy_of_tick = settings.total_energy_of_tick #self.number_vehicles*self.standard_batery_size
        self.total_evergy_of_simulation = settings.total_evergy_of_simulation#self.steps*self.total_energy_of_tick 
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
        self.step_time_sec = settings.step_time_milisec
        self.agent_list = []
        #storage available for PO
        self.storage_available = self.standard_batery_size*(self.number_vehicles/3) 
        self.energy_price_buy = settings.energy_price_buy
        self.energy_price_sell = settings.energy_price_sell
        self.current_step = 0
        self.prev_step = -1
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

    def start_simulation(self,map1,gui):
        self.architecture = "Test"
        self.current_step = 0
        #c = geographic_agent.geographic_agent(38.7414116,-9.143627785022142)
        #print(b.get_latitude())
        gui.disp_vehicles.setText(str(self.number_vehicles))
        gui.disp_stations.setText(str(self.number_stations))
        gui.disp_priority.setText(str(self.number_priority_vehicles))
        map1.clean_map()
        listToStr = ' '.join([str(elem) for elem in self.step_of_disaster])
        gui.disp_outages.setText(str(self.number_disasters)+" in ticks: "+listToStr)
        self.agent_list = []

    def do_step(self):
        self.do_step_arg = True
        pass

    def update(self, gui):
        loop = QEventLoop()
        QTimer.singleShot(self.step_time_sec, loop.quit)
        loop.exec_()
        if not self.stop_tog or self.do_step_arg:
            self.current_step += 1
            
        #self.current_step = current_step
        print(self.current_step)
        if (not self.stop_tog or self.do_step_arg) and self.prev_step != self.current_step:
            self.prev_step = self.current_step
            gui.disp_time.setText(str(self.current_step))
            gui.reload_map()
            self.do_step_arg = False

    def end(self, gui):
        gui.disp_time.setText("Complete")
        print("Complete")

    def plot(self,x,y):
        fig_energy, ax_energy = plt.subplots()
        #xerr = 5000*np.random.random_sample(20)
        #my_xticks = ['a', 'b', 'c', 'd']
        #plt.xticks(x, x)
        yerr = (statistics.mean(y) /4)*np.random.random_sample(len(y))
        ax_energy.errorbar(x, y,yerr=yerr,fmt='-o',marker='s', mfc='blue',
         mec='green',  ecolor='r')
        plt.axis([0, max(x), 0, (max(y)+max(yerr))])
        plt.ylabel('Energy available from source')
        plt.xlabel('Step')
        #plt.show()
        plt.savefig('graphs/Energy_Available_history.png')

    def graph(self):
        for agent in self.agent_list:
            if agent.name == "energy broker":
                self.energy_history = agent.energy_history
                self.plot(list(range(self.steps)), self.energy_history)
                break
            else:
                self.energy_history = "energy_history not found"
        #print(self.energy_history)
        

    def test(self,map1,gui):
        self.start_simulation(map1,gui)

       
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
        #b = charger_handler.charger_handler(lat,lng, map1, self.energy_price_buy, self.energy_price_sell)

        
        lng, lat = map1.get_random_point()
        d = power_operative.power_operative(lat,lng, self.storage_available, self)
        self.agent_list.append(d)

        lng, lat = map1.get_random_point()
        a = energy_broker.energy_broker(lat,lng,self.step_of_disaster,self.total_energy_of_tick, self.total_evergy_of_simulation, self,  self.step_of_redistribuition, self.max_flactuation, self.min_flactuation)
        self.agent_list.append(a)

        
        
        #agent_list.append(b)
        #agent_list.append(c)
        

        map1.add_agents(self.agent_list)
        
        
        while self.current_step < self.steps:
        #for current_step in range(self.steps):
            if not self.stop_tog or self.do_step_arg:
                a.act()
                #c.animate()
                d.act()




            self.update(gui)
        self.end(gui)  
        self.graph()
                   
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
        if not self.stop_tog:
            self.stop_tog = True
        else:
            self.stop_tog = False
        

