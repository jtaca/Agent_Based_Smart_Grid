import geographic_agent


class charger_handler(geographic_agent.geographic_agent):

	def __init__(self,lat,lng, map, energy_price_buy,energy_price_sell):
		geographic_agent.geographic_agent.__init__(self,lat,lng,'r', 'v',20)
		self.name = "charger handler"
		self.id = id
		self.map = map
		self.energy_available = 0 # you must ask PO , energy is for each step
		self.energy_price_buy = energy_price_buy
		self.energy_price_sell = energy_price_sell
		self.is_on = False
		self.vehicle_queue = []
		self.is_charging = False


		#if collective CH:
		#self. inside_stations these are geographic
		#self.energy per station
		#self.stations being used

	def act(self):

		pass

	#def give_energy_to_station(self): #collective only
	#	pass

	def toggle_on_off(self):
		pass

	def calculate_earnings(self):
		pass

	def message_drivers(self):
		pass

	def ask_for_energy(self):
		pass

	def report_spent_energy(self):
		pass

	#def forcast_energy_spendure(self): #for vehicles waiting

	def report_charge_time(self): #for each vehicle
		pass

	def charge_vehicle(self):
		pass



