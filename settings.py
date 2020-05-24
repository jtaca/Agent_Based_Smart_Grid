import random
############
# SETTINGS #
############

simulation_time = 300
nr_vehicles = 40
nr_stations = 20
nr_priority_vehicles = 7 # random.choice(range(self.number_vehicles)) #7
nr_disasters = 40
nr_redistribution = 50

draw_map = True #False #for way way better performance


max_source_flactuation = 1
min_source_flactuation = 0.6
standard_batery_size = 5000
max_battery = 0.3 # treshold for charging
total_energy_of_tick = (nr_vehicles/13)*standard_batery_size
total_evergy_of_simulation = simulation_time * total_energy_of_tick 
step_time_milisec = 0
energy_price_buy = 0.002
energy_price_sell = 0.01
storage_available = simulation_time *standard_batery_size*(nr_vehicles/3)

#ch_passive_spend_power = 1

#map
point = (38.736828, -9.138222) # IST
#point = (40.71427, -74.00597)

place = 'Alameda_buildings'
network_type='drive'
bldg_color='grey'
fig_height = 6
dpi=93 #93
dist=500
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

