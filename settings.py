import random
############
# SETTINGS #
############

simulation_time = 100
nr_vehicles = 40
nr_stations = 4
nr_priority_vehicles = 3 # random.choice(range(self.number_vehicles)) #7
nr_disasters = 6
nr_redistribution = 5

draw_map = True #False #for way way better performance
architecture = "N DA N CH \n 1 PO 1 EB"

max_source_flactuation = 1
min_source_flactuation = 0.6
standard_batery_size = 500
battery_percentage_spend_per_tick = 0.005
max_battery = 0.5 # treshold for charging
cost_per_tick = 30 # used for stations
total_energy_of_tick = (nr_vehicles/13)*standard_batery_size
total_evergy_of_simulation = simulation_time * total_energy_of_tick 
step_time_milisec = 0
energy_price_buy = 0.002
energy_price_sell = 0.01
storage_available = simulation_time *standard_batery_size*(nr_vehicles/3)

charger_flow = 100
tax = 0.4

#ch_passive_spend_power = 1

#map
point = (38.736828, -9.138222) # IST
#point = (40.71427, -74.00597) #ny
#point = (48.855216, 2.345615) #paris
#point = (51.501134, -0.141112) # london

place = 'Alameda_buildings'
network_type='drive'
bldg_color='grey'
fig_height = 6
dpi=93 #93
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


