import geographic_agent
import map

import networkx as nx
import numpy as np
import osmnx as ox

class driver_assistant(geographic_agent.geographic_agent):

    def __init__(self, origin, route, battery, map, is_priority):
        self.name = "driver assistant"
        self.battery = battery
        self.velocity = 0.1
        self.accelaration = 0
        self.is_priority = is_priority

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

        #se precisa de ser carregado faz display numa cor diferente
        
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

        #View
        self.car_view = self.determine_view() #Gives the next 3 nodes_coordenates, what the car sees
        
        
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

    def act(self):
        pass

    def animate(self):
        self.update_current_route()
        dt = 1/1000
        
        self.x = self.x + self.velocity * dt
        self.y = self.y + self.velocity * dt
        self.lng = self.lng + self.velocity * dt
        self.lat = self.lat + self.velocity * dt
        self.set_latitude(self.lat)
        self.set_longitude(self.lng)
        #print("c")
        #print("Longitude")
        #print(self.get_longitude())
        #print("Latitude")
        #print(self.get_latitude())

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
        else:
            #Route ended, change route
            self.route_idx += 1
            self.current_route = self.list_route[self.route_idx % 3]
            self.origin = self.current_route[0]
            self.destination = self.current_route[len(self.current_route)-1]
            self.path = get_path(self.G, self.origin, self.destination)
            self.xpath = np.array([self.path[i][0] for i in range(len(self.path))])
            self.ypath = np.array([self.path[i][1] for i in range(len(self.path))])
            
        
            
    #TODO: Test this
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
        if self.view:
            if self.crossed_node_event():
                if len(self.view) >= 2:
                    return self.view[1]
                else:
                    return get_coordinates_of_node(self.G, self.destination)
            else:
                return self.view[0]
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
