import geographic_agent
import map

import networkx as nx
import numpy as np
import osmnx as ox

class driver_assistant(geographic_agent.geographic_agent):

    def __init__(self, origin, route, battery, map, is_priority, id, time_u, price_u, distance_u):
        #Generic Attributes
        self.id = id
        self.name = "driver assistant"
        self.battery = battery
        self.velocity = [0.1, 0.1]
        self.velocityx = self.velocity[0]
        self.velocityy = self.velocity[1]
        self.accelaration = 0
        self.is_priority = is_priority
        self.is_charging = False
        self.needs_charge = False
        self.time_to_wait = 0

        #Agent has the map
        self.map = map
        self.G = map.get_map()

        #Route and Coordenates
        self.list_route = route
        self.current_node = origin
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
    def init_da_list(self, ch):
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

        if len(self.plan)>0 and self.succeededIntention() and not self.impossibleIntention():
            action = self.plan.pop(0)
            if self.isPlanSound(action):
                self.execute(action)
            else:
                self.rebuildPlan()
            
            if self.reconsider():
                self.deliberate()
            
        else:
            self.deliberate()
            self.buildPlan()
            self.agentReactiveDecision()

        #consume_battery
        #check battery
        #if battery low
            #communicate ch to ask for station
        #check Messages
            # if battery low and messages have charging station
                #Select charging station
                #clean messages
            # if battery not low and messages have charging stations
                #Decide to charge
                #clean messages
        #if decide to charge
            #change route
        
        #animate

        if self.battery == 0:
            #stop
            #return
            pass

        self.battery -= 1
        
        messages = self.check_for_messages()
        if self.battery_low() and not messages.any():
            self.ask_for_stations()
            self.animate()
            return
        
        if messages.any():
            pass
            #Decide to or not charge
            #If yes
                #Update to CH
                #Update to DA
                #Update route <- MAJOR PROBLEM!
            #If no 
                #Nothing happens
        
        #animate

    #
    # 
    #  D E L I B A R A T I V E   A R Q U I T E C T U R E
    # 
    # 

    def updateBeliefs(self):
        self.battery -= 10
        if self.is_charging:
            self.time_to_wait = self.ask_for_time()

    def succeededIntention(self): # TODO: Nao sei bem isto
        if self.intention == 'On route':
            return True
        elif self.intention == 'Go charge':
            return True
        elif self.intention == 'Charging':
            return True
        elif self.intention == 'Waiting':
            return True
        elif self.intention == 'Stop':
            return True
        else:
            return False

    def impossibleIntention(self):
        return False

    def isPlanSound(self, action):
        return True

    def execute(self, action):
        if action == 'move':
            self.animate()
        
        elif action == 'decide station':
            self.options = self.check_options()
            self.charging_station = self.decide()
            
            self.update_ch_time()
            return

        elif action == 'go to station':
            #Update route
            self.animate() #with new route until arriva
            #say I arrived
            #wait until car is charged
            pass
        
        elif action == 'arrived':
            self.charging_station.add_da_to_queue(self)
        
        elif action == 'wait':
            pass

        elif action == 'return':
            #Update car route to the normal route
            self.animate() #until arrival
            #restart the route
            pass

        '''
        elif action == 'decide':
            #check options
            #Decide if yes or no charge
            #If yes
                #BID Charger Hanlder
                #Update route
            self.animate() #with new route until arrival
            #wait until car is charged
            pass
        '''

    def rebuildPlan(self):
        pass

    def reconsider(self):
        pass

    def deliberate(self):
        self.current_desires = []

        #TOP Priority
        if self.battery_low():
            self.current_desires.append('Go charge')
        
        if self.options.any() and not self.car_charged(): #If has charger Handler proposals
            self.current_desires.append('Decide to charge')
        
        if self.car_charged():
            self.current_desires.append('Return to Route')

        if not self.battery_low():
            self.current_desires.append('On route')
        
        self.intention = self.current_desires[0]

    def buildPlan(self):
        self.plan = []

        if self.intention == 'Go Charge':
            self.plan.append('go charge')

        elif self.intention == 'Decide to charge':
            self.plan.append('decide')
        
        elif self.intention == 'On route':
            self.plan.append('move')

        elif self.intention == 'Return to Route':
            self.plan.append('return')
        
    def agentReactiveDecision(self):
            self.animate()


    # 
    # 
    #  A N I M A T E
    # 
    # 

    def animate(self):
        self.update_current_route()
        dt = 1/1000
        
        self.x = self.x + self.velocityx * dt
        self.y = self.y + self.velocityy * dt
        self.lng = self.lng + self.velocity * dt
        self.lat = self.lat + self.velocity * dt
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
                #Path maintains nothing happens
                pass
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

      
    def battery_low(self):
        return self.battery < 300

    def check_for_messages(self):
        pass

    def respond_CH(self):
        pass

    def update_DAs(self):
        pass

    def update_route(self):
        pass

    def decide(self):
        #return an option
        #opt = (Time, Position, Price, CHid)
        best = [0, 0] # [Time or Distance or Price, Chid] 
        for opt in self.options:
            if self.distance_u >= self.time_u and self.distance_u >= self.price_u:
                dist = calculate_distance(opt[1], current_position)
                if dist <= best[0]:
                    best[1] = opt[3]
            
            elif self.time_u >= self.distance_u and self.time_u >= self.price_u:
                if opt[0] <= best[0]:
                    best[1] = opt[3]

            elif self.price_u >= self.distance_u and self.price_u >= self.time_u:
                if opt[2] <= best[0]:
                    best[1] = opt[3]
    
        ch = None
        for i in range(len(self.ch_list)):
            if best[1] == self.ch_list[i]:
                ch = self.ch_list[i]
        
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

    def uptade_ch_time(self):
        position = self.charging_station.get_position()
        distance = calculate_distance(position, current_position)
        time = calculate_time(distance, self.velocity)
        self.time_of_travel = time
            
    
    def receive_proposal(self, proposal):
        self.proposals.append(proposal)

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
