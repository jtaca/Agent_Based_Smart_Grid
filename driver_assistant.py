import geographic_agent

import map

import networkx as nx
import numpy as np
import osmnx as ox
import matplotlib

class driver_assistant(geographic_agent.geographic_agent):

	def __init__(self, origin, route, battery, map, is_priority):

		

		self.name = "driver assistant"
		self.batery = battery
		self.velocity = 0
		self.accelaration = 0
		self.is_priority = is_priority
		

		#Agent has the map
		self.map = map
		self.G = map.get_map()

		#Route and Coordenates
		self.route = route
		self.current_node = origin
		self.lng = self.G.nodes[origin]['x']
		self.lat = self.G.nodes[origin]['y']
		if is_priority:
			geographic_agent.geographic_agent.__init__( self, self.lat , self.lng,'b','o',10,3)
		else:
			geographic_agent.geographic_agent.__init__( self, self.lat , self.lng,'g','o',10,3)
		

	def animate(self):
		pass




def get_route(G, origin, destination):
    """
    acquires the typical node-based route list from NetworkX with weight=length

    :param      origin: node ID
    :param destination: node ID
    :return:     route: list of intersection nodes
    """
    return nx.shortest_path(G, origin, destination, weight='length')

def get_init_path(G, origin, destination):
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
