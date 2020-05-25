import geographic_agent
import map

import time
import networkx as nx
import numpy as np
import osmnx as ox

class driver_assistant(geographic_agent.geographic_agent):

    def __init__(self, origin, route, initial_battery, max_battery_capacity, battery_threshold, battery_spent, map, is_priority, id, time_u, price_u, distance_u, simulation):
        #Generic Attributes
        self.id = id
        self.name = "driver assistant"
        self.is_priority = is_priority
        self.is_charging = False
        self.time_to_wait = 0
        self.need_charge = False
        self.simulation = simulation
        
        #Battery stuff
        self.battery = initial_battery
        self.battery_threshold = battery_threshold * max_battery_capacity
        self.max_battery_capacity = max_battery_capacity
        self.battery_spent_per_tick = self.max_battery_capacity * battery_spent
        self.battery_needed = self.max_battery_capacity - self.battery
        self.died = False

        #Agent has the map
        self.map = map
        self.G = map.get_map()

        #Route and Coordenates
        self.list_route = route
        self.lng = self.G.nodes[origin]['x']
        self.lat = self.G.nodes[origin]['y']
        if is_priority:
            geographic_agent.geographic_agent.__init__(self, self.lat, self.lng, 'b', 'o', 20, 2)
        else:
            geographic_agent.geographic_agent.__init__(self, self.lat, self.lng, 'g', 'o', 20, 2)
        
        #For Animation
        self.route_idx = 0
        self.current_route = self.list_route[0]
        self.current_node = origin
        self.last_destination = self.current_route[-1]

        #Environment View
        self.car_view = self.determine_view() #Gives the next 3 nodes_coordenates, what the car sees
        self.da_list = []  #List of Driver Assistants
        self.ch_list = []  #List of Charger Handlers
        self.emotional_dict = self.init_emotional_dict()
    
        self.options = []
        self.charging_station = None #CH of choice
        self.proposals = []

        #Deliberative and Emotional
        self.time_u = time_u
        self.price_u = price_u
        self.distance_u = distance_u
        
        self.desires = ['On route', 'Go charge', 'Charging', 'Waiting', 'Stop']
        self.actions = ['move', 'change route', 'charge', 'wait']
        self.plan = []
        self.intention = 'On route' #Car must start with battery
        self.current_desires = []

    #
    # 
    #   I N T I T I A L I Z E R S
    #
    #  
    
      
    #Initialize the Driver Assistants List
    def init_da_list(self, da):
        self.da_list = da
    
    #Initialize the Charger Handlers List
    def init_ch_list(self, ch):
        self.ch_list = ch

    #Initialize the emotional dict
    def init_emotional_dict(self):
        #emotions are a list of values between 0 and 1
        emotions = self.generate_emotions()
        i = 0
        for ch in ch_list:
            self.emotional_dict[ch.id] = emotions[i]
            i += 1

    def generate_emotions(self):
        emotions = np.random.randint(low=0, high=5, size=len(self.ch_list))

    #
    # 
    #  A C T
    # 
    # 

    def act(self):

        self.updateBeliefs()

        print('DA'+str(self.id)+': My battery = '+str(self.battery))

        if len(self.plan)>0 and self.succeededIntention() and not self.impossibleIntention():
            action = self.plan[0]
            if self.isPlanSound(action): #Always true
                print("DA "+str(self.id)+": My action " + action)
                action = self.plan.pop(0)
                self.execute(action)
            else:
                self.rebuildPlan(action)  
            
            if self.reconsider():
                self.deliberate()
                self.buildPlan()
            
        else:
            self.deliberate()
            self.buildPlan()
            self.agentReactiveDecision()

        
    #
    # 
    #  D E L I B A R A T I V E   A R Q U I T E C T U R E
    # 
    # 

    def updateBeliefs(self):
        if self.is_car_charging():
            self.time_to_wait = self.ask_for_time()
        
        else:
            if self.battery <= 0:
                self.died = True

            else:
                self.died = False
                self.battery -= self.battery_spent_per_tick
                self.battery_needed = self.max_battery_capacity - self.battery

            if self.low_battery():
                print("DA "+str(self.id)+": BATTERY IS LOW")
                self.need_charge = True
            else:
                self.need_charge = False

        

    def deliberate(self):
        self.current_desires = []

        print("DA "+str(self.id)+":Deliberate")

        #TOP Priority
        if any(self.proposals) and not self.is_car_charging() and self.need_charge and not self.died:
            ch_Id = self.charging_station.id()
            new_ch = change_station() 
            if new_ch == None:
                self.current_desires.append('Continue')

            elif new_ch.id() != ch_Id: #There is a better option
                self.charging_station = new_ch
                self.proposals.clear()
                self.current_desires.append('Change station')

        elif self.need_charge and self.died:
            self.current_desires.append('Die')

        elif self.need_charge:
            print("DA "+str(self.id)+":My desire to charge")
            self.current_desires.append('Go charge')
        
        elif not self.need_charge:
            self.current_desires.append('On route')
        
        self.intention = self.current_desires[0]

    def succeededIntention(self): #Always successfull
        return True

    def impossibleIntention(self): #Always possible
        return False

    def buildPlan(self):
        if self.intention == 'Continue':
            return
        
        self.plan = []

        if self.intention == 'Go charge':
            self.plan.append('decide station')
            self.plan.append('go to station')
            self.plan.append('move')
            self.plan.append('arrived')
            self.plan.append('wait')
            self.plan.append('return')
            self.plan.append('move')
            self.plan.append('resume route')
                      
        elif self.intention == 'Change station':
            #Already changed station
            self.plan.append('go to station')
            self.plan.append('move')
            self.plan.append('arrived')
            self.plan.append('wait')
            self.plan.append('return')
            self.plan.append('move')
            self.plan.append('resume route')
                    
        elif self.intention == 'On route':
            self.plan.append('move normaly')
        
        elif self.intention == 'Die':
            self.plan.append('stop')


    def isPlanSound(self, action):
        if action == 'arrived':
            return agent_has_arrived(self.current_node, self.destination)
        
        elif action == 'return':
            return not self.is_car_charging()
        
        elif action == 'resume route':
            return agent_has_arrived(self.current_node, self.destination)
        
        else:
            return True
    
    def execute(self, action):
        if action == 'move normaly':
            self.teleport(action)
        
        elif action == 'move':
            self.teleport(action)
        
        elif action == 'decide station':
            print("DA "+str(self.id)+": Deciding station")
            self.options = self.check_options()
            self.charging_station = self.decide()
            
            if self.charging_station != None:
                print(self.charging_station.id)

                self.update_time_travel()
                self.charging_station.add_da_to_queue_inc(self)

        elif action == 'go to station':
            self.teleport(action)
        
        elif action == 'arrived':
            self.charging_station.remove_da_to_queue_inc(self)
            self.charging_station.add_da_to_queue(self)
        
        elif action == 'wait':
            self.map.add_points_to_print((self.get_longitude(),self.get_latitude()),'y','+',20)
            self.simulation.number_cars_charging[self.simulation.current_step] += 1
            print("DA id: %d is charging on station %d" , self.id, self.charging_station.id)

        elif action == 'return':
            self.charging_station = None
            self.teleport(action)
        
        elif action == 'resume route':
            self.route_idx += 1    
            self.current_route = self.list_route[self.route_idx % 3]
            self.destination = self.current_route[-1]
        
        elif action == 'stop':
            self.map.add_points_to_print((self.get_longitude(),self.get_latitude()),'k','o',20)
            self.simulation.number_cars_without_energy[self.simulation.current_step] += 1
            self.teleport(action)


    def rebuildPlan(self, action):
        new_action = 'action'

        if action == 'arrived' or action == 'resume route':
            self.plan.insert(0, 'move')
        
        elif action == 'return':
            self.plan.insert(0, 'wait')
        

    def reconsider(self):
        if self.died:
            return True

        if any(self.proposals) and not self.is_car_charging():
            return True
        
        if self.need_charge and self.charging_station == None:
            print('I NEED CHARGE')
            return True
        
        return False

    def agentReactiveDecision(self):
            self.teleport('move normaly')


    # 
    # 
    #  A N I M A T E
    # 
    # 

    def teleport(self, action):
        if action == 'stop':
            print('DA: Out of Battery')
            return

        #Car is back on normal route
        if (self.current_node == self.destination and action == 'move normaly'):
            self.route_idx += 1    
            self.current_route = self.list_route[self.route_idx % 3]
            self.destination = self.current_route[-1]

        elif self.current_node == self.destination and action == 'move':
            return

        if action == 'go to station':
            self.last_destination = self.destination
            ch_node = self.charging_station.get_node_position()
            route = nx.shortest_path(self.G, self.current_node, ch_node, weight='length')
            self.current_route = route
            self.destination = self.current_route[-1]
        
        elif action == 'return':
            route = nx.shortest_path(self.G, self.current_node, self.last_destination, weight='length')
            self.current_route = route
            self.destination = self.current_route[-1]
        
        #Move the car accordingly to a route
        self.lng, self.lat = get_coordinates_of_node(self.G, self.current_node)
        self.set_latitude(self.lat)
        self.set_longitude(self.lng)
        
        try:
            self.current_route = self.current_route[1:]
            self.current_node = self.current_route[0]           
        except:
            self.current_node = self.destination
      
    def low_battery(self):
        return self.battery <= self.battery_threshold 
    
    def update_charged(self, state):
        self.is_charging = state

    def is_car_charging(self):
        return self.is_charging
    
    #
    #   Decide Station and Change Station
    #

    def decide(self):
        #Wort Wort Wort
        worst_time_to_wait = 1
        worst_distance = 1
        worst_price = 1

        #opt = (Time, Node, Price, CH_id)
        print(self.options)
        for opt in self.options:
            #Calulate worst time
            if opt[0] >= worst_time_to_wait:
                worst_time_to_wait = opt[0]
            
            dist = calculate_distance(self.G, opt[1], self.current_node)
            if dist >= worst_distance:
                worst_distance = opt[1]
            
            if opt[2] >= worst_price:
                worst_price = opt[2]
            
        ch_ratings = {}
        for opt in self.options:    
            relative_time_to_wait = 1/((opt[0]+1)/worst_time_to_wait)  
            
            dist = calculate_distance(self.G, opt[1], self.current_node)
            relative_distance = 1/(dist/worst_distance)
            
            relative_price = 1/(opt[2]/worst_price)

            station_rating = self.time_u * relative_time_to_wait + self.price_u * relative_price + self.distance_u * relative_distance
            if self.is_possible_to_arrive(dist):
                ch_ratings[opt[3]] = station_rating
            
            elif self.is_possible_to_arrive(dist) and (dist == -1):
                ch_ratings[opt[3]] = -1
            
            else: #Not enough battery it will die
                ch_ratings[opt[3]] = 0

        best_rating = -1
        best_id = 0
        for id in ch_ratings.keys():
            if ch_ratings[id] >=  best_rating:
                best_rating = ch_ratings[id]
                best_id = id

        if best_rating == -1:
            return None #Impossivel de calcular rota
        
        ch = None
        for i in range(len(self.ch_list)):
            if best_id == self.ch_list[i].id:
                ch = self.ch_list[i]
        
        return ch 


    def change_station(self):
        #Wort Wort Wort
        worst_time_to_wait = 1
        worst_distance = 1
        worst_price = 1

        #opt = (Time, Node, Price, CH_id)
        for opt in self.proposals:
            #Calulate worst time
            if opt[0] >= worst_time_to_wait:
                worst_time_to_wait = opt[0]
            
            dist = calculate_distance(self.G, opt[1], self.current_node)
            if dist >= worst_distance:
                worst_distance = opt[1]
            
            if opt[2] >= worst_price:
                worst_price = opt[2]
            
        ch_ratings = {}
        for opt in self.proposals:    
            relative_time_to_wait = 1/(opt[0]/worst_time_to_wait)  
            
            dist = calculate_distance(self.G, opt[1], self.current_node)
            relative_distance = 1/(dist/worst_distance)
            
            relative_price = 1/(opt[2]/worst_price)

            station_rating = self.time_u * relative_time_to_wait + self.price_u * relative_price + self.distance_u * relative_distance
            if self.is_possible_to_arrive(dist):
                ch_ratings[opt[3]] = station_rating
            
            elif self.is_possible_to_arrive(dist) and (dist != -1):
                ch_ratings[opt[3]] = -1
            
            else: #Not enough battery it will die
                ch_ratings[opt[3]] = 0

        best_rating = -1
        best_id = 0
        for id in ch_ratings.keys():
            if ch_ratings[id] >=  best_rating:
                best_rating = ch_ratings[id]
                best_id = id

        if best_rating == -1:
            return None #Impossivel de calcular rota

        ch = self.charging_station
        if best_id != ch.id():
           for i in range(len(self.proposals)):
               if best_id == self.proposals[i].id():
                   ch = self.proposals[i]
        
        return ch 
        
        
    #
    #   Communication with Charger Handlers
    #

    def ask_for_time(self):
        total_time = 0 
        for i in range(len(self.ch_list)):
            total_time += self.ch_list[i].get_time_of_wait() + self.ch_list[i].calculate_time_to_charge()
        return total_time
    
    def check_options(self):
        options = []
        for i in range(len(self.ch_list)):
            options.append(self.ch_list[i].get_option())
        return options

    def update_time_travel(self):
        node = self.charging_station.get_node_position()
        distance = calculate_distance(self.G, node, self.current_node)
        time = calculate_time(distance)
        self.time_of_travel = time
            
    def receive_proposal(self, proposal):
        self.proposals.append(proposal)
   
    def is_possible_to_arrive(self, dist):
        if dist == -1:
            return False
        
        else:
            time = calculate_time(dist)
            battery_required = self.battery_spent_per_tick * time
            if self.battery >= battery_required:
                return True
            
            else:
                return False

        return False

#         
#           A U X I L I A R   F U N C T I O N S 
#
def get_coordinates_of_node(G, node):
    coord = np.array([G.nodes[node]['x'], G.nodes[node]['y']])
    return coord

def agent_has_arrived(node1, node2):
    return node1 == node2

def calculate_distance(G, node1, node2):
    try:
        route = nx.shortest_path(G, node1, node2, weight='length')
        return len(route)
    except nx.exception.NodeNotFound:
        return -1 
    except nx.exception.NetworkXNoPath:
        return -1

def calculate_time(distance):
    return distance #Since agent travels one node per tick
