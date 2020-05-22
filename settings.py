import random
############
# SETTINGS #
############

simulation_time = 20
nr_vehicles = 10
nr_stations = 2
nr_priority_vehicles = 3 # random.choice(range(self.number_vehicles)) #7
nr_disasters = 3
nr_redistribution = 7

max_source_flactuation = 1
min_source_flactuation = 0.6
standard_batery_size = 5000
total_energy_of_tick = nr_vehicles*standard_batery_size
total_evergy_of_simulation = simulation_time * total_energy_of_tick 
step_time_milisec = 1000
energy_price_buy = 0.002
energy_price_sell = 0.01


#map
point = (38.736828, -9.138222) # IST

place = 'Alameda_buildings'
network_type='drive'
bldg_color='grey'
fig_height = 6
dpi=93
dist=1000
default_width=4
street_widths = {'footway' : 0.5,
                'steps' : 0.5,
                'pedestrian' : 0.5,
                'path' : 0.5,
                'track' : 0.5,
                'service' : 2,
                'residential' : 3,
                'primary' : 5,
                'motorway' : 6}

