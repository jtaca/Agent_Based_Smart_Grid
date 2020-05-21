import matplotlib
matplotlib.use("Agg")
import networkx as nx
import numpy as np
import osmnx as ox
import settings 

import matplotlib.backends.backend_agg as agg


def make_plot(G):
        
    ec = ['grey' if data['oneway'] else '#e0e0e0' for u, v, key, data in G.edges(keys=True, data=True)]

    #ex
    #(38.7414116, -9.143627785022142)
    lat = 38.7414116
    lng = -9.143627785022142

    # get nearest node incident to nearest edge to reference point
    geom, u, v = ox.get_nearest_edge(G, (lat, lng))
    nn = min((u, v), key=lambda n: ox.great_circle_vec(lat, lng, G.nodes[n]['y'], G.nodes[n]['x']))
   
    fig, ax = ox.plot_graph(G, fig_height=settings.fig_height, node_size=0, edge_color=ec, edge_linewidth=0.5, show=False, close=False, save=False,
    filename=settings.place)


    ax.scatter(lng, lat, c='r', marker='x')
    ax.scatter(G.nodes[nn]['x'], G.nodes[nn]['y'], c='r', s=50, zorder=2)

    canvas = agg.FigureCanvasAgg(fig)
    canvas.draw()
    renderer = canvas.get_renderer()
    raw_data = renderer.tostring_rgb()
    size = canvas.get_width_height()

    return fig, ax, raw_data, size






class map:
    def __init__(self):
        self.img_folder = 'images'
        self.extension = 'png'
        self.size = 600
        self.G = ox.graph_from_point(settings.point,distance=settings.dist, distance_type='bbox', network_type=settings.network_type)
        ec = ['grey' if data['oneway'] else '#e0e0e0' for u, v, key, data in self.G.edges(keys=True, data=True)]
        self.fig, self.ax = ox.plot_graph(self.G, fig_height=settings.fig_height, node_size=0, edge_color=ec, edge_linewidth=0.5, show=False, 
        close=False, save=False, filename=settings.place)
        #plt.savefig(settings.place)


    def reload_frame(self):
        self.fig, self.ax, raw_data, size  = make_plot(self.G)
        return raw_data, size

       








import pylab

fig = pylab.figure(figsize=[4, 4], # Inches
                   dpi=100,        # 100 dots per inch, so the resulting buffer is 400x400 pixels
                   )
ax = fig.gca()
ax.plot([1, 2, 4])

canvas = agg.FigureCanvasAgg(fig)
canvas.draw()
renderer = canvas.get_renderer()
raw_data = renderer.tostring_rgb()

map1 = map()
#map1.reload_frame()

import pygame
from pygame.locals import *

pygame.init()

window = pygame.display.set_mode((600, 400), DOUBLEBUF)
screen = pygame.display.get_surface()

size = canvas.get_width_height()

surf = pygame.image.fromstring(map1.reload_frame()[0], map1.reload_frame()[1], "RGB")
screen.blit(surf, (0,0))
pygame.display.flip()

crashed = False
while not crashed:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			crashed = True
