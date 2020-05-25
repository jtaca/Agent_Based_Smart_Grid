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
        self.velocity = [1, 1]
        self.velocityx = 0 #self.velocity[0]
        self.velocityy = 0 #self.velocity[1]
        self.accelaration = 0
        self.is_priority = is_priority
        self.is_charging = False
        self.needs_charge = False
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
        self.x = self.lng
        self.y = self.lat
        self.current_route = self.list_route[0]
        self.current_node = origin
        self.last_destination = self.current_route[-1]

        self.origin = origin
        self.destination = self.current_route[len(self.current_route)-1]
        self.path = get_path(self.G, self.origin, self.destination)
        self.xpath = np.array([self.path[i][0] for i in range(len(self.path))])
        self.ypath = np.array([self.path[i][1] for i in range(len(self.path))])

        #Environment View
        self.car_view = self.determine_view() #Gives the next 3 nodes_coordenates, what the car sees
        self.da_list = []  #List of Driver Assistants
        self.ch_list = []  #List of Charger Handlers
    
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

    def determine_view(self):
        """
        this method handles the exception where the path is shorter than look_ahead_nodes

        :return view: list or bool: list of nodes immediately ahead of the car or False if end of route
        """
        look_ahead_nodes = 3
        xpath, ypath = self.xpath, self.ypath
        if xpath.any() and ypath.any():
            x, y = xpath[:look_ahead_nodes], ypath[:look_ahead_nodes]
            return [(x[i], y[i]) for i in range(len(x))]
        else:
            return False

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
        
        self.current_route = self.current_route[1:]
        self.current_node = self.current_route[0]
        

    def animate(self):
        self.update_current_route()
        dt = 1/1000
        
        self.x = self.x + self.velocityx * dt
        self.y = self.y + self.velocityy * dt
        self.lng = self.lng + self.velocityx * dt
        self.lat = self.lat + self.velocityy * dt
        self.set_latitude(self.lat)
        self.set_longitude(self.lng)
        
        self.determine_view()
        
    def update_current_route(self):
        xpath, ypath = self.xpath, self.ypath
        if xpath.any() and ypath.any():
            #determine if the car has just crossed a node
            if self.crossed_node_event():
                self.xpath = xpath[1:]
                self.ypath = ypath[1:]
                #new_xpaths.append(xpath[1:])
                #new_ypaths.append(ypath[1:])
            else:
                self.xpath = xpath
                self.ypath = ypath
                #Path maintains nothing happens
                #new_xpaths.append(xpath)
                #new_ypaths.append(ypath)
            
            next_node = np.array(self.upcoming_node_coordinates())
            position = np.array((self.x, self.y))

            velocity_direction = unit_vector(next_node - position)
            self.velocity = velocity_direction * self.velocity

            self.velocityx = self.velocity[0]
            self.velocityy = self.velocity[1]


        else:
            #Route ended, change route
            self.route_idx += 1
            self.current_route = self.list_route[self.route_idx % 3]
            self.origin = self.current_route[0]
            self.destination = self.current_route[len(self.current_route)-1]
            self.path = get_path(self.G, self.origin, self.destination)
            self.xpath = np.array([self.path[i][0] for i in range(len(self.path))])
            self.ypath = np.array([self.path[i][1] for i in range(len(self.path))])

      
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
    def crossed_node_event(self):
        """
        Determines if the car has crossed a node, and advises simulation to change
        its velocity vector accordingly

        :return bool: True if the car is passing a node, False otherwise
        """
        car_near_xnode = np.isclose(self.car_view[0][0], self.x, rtol=1.0e-6)
        car_near_ynode = np.isclose(self.car_view[0][1], self.y, rtol=1.0e-6)

        if car_near_xnode and car_near_ynode:
            return True
        else:
            return False

    def upcoming_node_coordinates(self):
        """
        Determines the coordinates of the next node in view

        :return view: tuple: returns upcoming node coords in the path
        """
        if self.car_view:
            if self.crossed_node_event():
                if len(self.car_view) >= 2:
                    return self.car_view[1]
                else:
                    return get_coordinates_of_node(self.G, self.destination)
            else:
                return self.car_view[0]
        else:
            # end of route
            return get_coordinates_of_node(self.G, self.destination)
          

def get_path(G, origin, destination):
    """
    compiles a list of tuples which represents a route

    Parameters
    __________
    :param      origin: int:    node ID
    :param destination: int:    node ID

    Returns
    _______
    :return path: list where each entry is a tuple of tuples
    """
    lines = shortest_path_lines_nx(G, origin, destination)
    path = path_decompiler(lines)
    return path

def shortest_path_lines_nx(G, origin, destination):
    """
    uses the default shortest path algorithm available through networkx

    Parameters
    __________
    :param      origin: int:    node ID
    :param destination: int:    node ID

    Returns
    _______
    :return lines: list:
        [(double, double), ...]:   each tuple represents the bend-point in a straight road
    """

    route = nx.shortest_path(G, origin, destination, weight='length')

    # find the route lines
    edge_nodes = list(zip(route[:-1], route[1:]))
    lines = []
    for u, v in edge_nodes:
        # if there are parallel edges, select the shortest in length
        data = min(G.get_edge_data(u, v).values(), key=lambda x: x['length'])

        # if it has a geometry attribute (ie, a list of line segments)
        if 'geometry' in data:
            # add them to the list of lines to plot
            xs, ys = data['geometry'].xy
            lines.append(list(zip(xs, ys)))
        else:
            # if it doesn't have a geometry attribute, the edge is a straight
            # line from node to node
            x1 = G.nodes[u]['x']
            y1 = G.nodes[u]['y']
            x2 = G.nodes[v]['x']
            y2 = G.nodes[v]['y']
            line = ((x1, y1), (x2, y2))
            lines.append(line)

    return lines

def path_decompiler(lines):
    """
    Decompiles a path from its geometry configuration into a pure list of tuples

    :param  lines:      list in geometric form according to osmnx 'geometry' feature
    :return new_path:   list of tuples
    """
    path = []
    for line in lines:
        for point in line:
            path.append(point)

    # the path must be cleaned of twin nodes for car dynamics
    # these are nodes which overlap (two nodes laying on top of each other on the same point)
    # OpenStreetMap has this issue
    clean_path = []
    for i in range(len(path)):
        if (i < len(path) - 1) and (path[i] != path[i + 1]):
            clean_path.append(path[i])
    clean_path.append(path[-1])
    return clean_path


def get_coordinates_of_node(G, node):
    """
    Get latitude and longitude given node ID

    :param node:      graphml node ID
    :return position: array:    [latitude, longitude]
    """
    # note that the x and y coordinates of the G.nodes are flipped
    # this is possibly an issue with the omnx G.load_graphml method
    # a correction is to make the position tuple be (y, x) as below
    coord = np.array([G.nodes[node]['x'], G.nodes[node]['y']])
    return coord

def unit_vector(vector):
    """ Returns the unit vector of the vector """
    return vector / np.linalg.norm(vector)

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

#Help Functions

		#ox.plot_graph(G, fig_height=10, fig_width=10, edge_color="black")


		#---DEPRACATED---
		#A = self.map.get_random_node()
		#B = self.map.get_random_node()
		#C = self.map.get_random_node()
		#self.route = (A,B,C)
		#print(self.route)
		#xA = G.nodes[A]['x']
		#ox.plot_graph_route(G, route, fig_height=10, fig_width=10)
		#ox.plot_graph_routes(self.G, self.route)
