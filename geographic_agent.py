import osmnx as ox

class geographic_agent:
    
        def __init__(self, lat, lng, get_color,get_marker, get_size):
            self.lng = lng
            self.lat = lat
            #for the map
            self.get_color = get_color
            self.get_marker = get_marker
            self.get_size = get_size

        def get_latitude(self):
            return self.lat


        def get_longitude(self):
            return self.lng

        def get_closest_node(self,G ):
            nodes, _ = ox.graph_to_gdfs(G)

            geom, u, v, marosca = ox.get_nearest_edge(G, (self.lat, self.lng))
            nn = min((u, v), key=lambda n: ox.great_circle_vec(self.lat, self.lng, G.nodes[n]['y'], G.nodes[n]['x']))

            return G.nodes[nn]['x'], G.nodes[nn]['y']