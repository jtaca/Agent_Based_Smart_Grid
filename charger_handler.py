import geographic_agent
import math


class charger_handler(geographic_agent.geographic_agent):

	def __init__(self, lat, lng, map, energy_price_buy, energy_price_sell, po):
		geographic_agent.geographic_agent.__init__(self,lat,lng,'r', 'v',20,2)
		self.name = "charger handler"
		self.id = id
		self.map = map
		self.energy_available = 0 # you must ask PO, energy is for each step
		self.energy_price_buy = energy_price_buy
		self.energy_price_sell = energy_price_sell
		self.is_charging = False


		#if collective CH:
		#self. inside_stations these are geographic
		#self.energy per station
		#self.stations being used

		#deliberative
		self.desires = ['bid_da', 'negotiate_po']
		self.actions = ['bid_da', 'negotiate_po', 'give', 'receive']
		self.plan = []
		self.intention = 'store' #TODO
		self.current_desires =[]

		#negotiation/bid
		self.da_queue = []
		self.po = po
		self.bid_result = -1

		'''
		duvidas
		tem de receber o po
		tem de receber o numero total de ticks
		tem de receber o ch_passive_spend_energy
		quanta energia posso carregar o carro por tick?
		po:
		- tem de ter um método que devolve se pode negociar, ou se ainda tem acumulated_energy para negociar
		'''


	# DA calls this when needs energy
	def add_da_to_queue(self, da):
		self.da_queue.append(da)


	#def updateBeliefs(self):
	#	self.ask_for_spending_report()


	def succeededIntention(self): #igual ao isPlanSound()
		if self.intention == 'bid_da':
			return len(self.da_queue) > 0
		elif self.intention == 'negotiate_po':
			return self.po.get_acumulated_energy > 0
		elif self.intention == 'give':
			return self.energy_available > 0 and self.bid_result > 0
		elif self.intention == 'store':
			#TODO
			#return (self.acumulated_energy < self.storage_available and self.available_for_tick >0 )
			return True
		else:
			return False


	def impossibleIntention(self):
		#for now nothing is impossible
		return False


	def isPlanSound(self,action):
		if action == 'bid_da':
			return len(self.da_queue) > 0
		elif action == 'negotiate_po':
			return self.po.acumulated_energy > 0
		elif action == 'give':
			return self.energy_available > 0 and self.bid_result > 0
		elif action == 'receive':
			#TODO
			#return (self.acumulated_energy < self.storage_available and self.available_for_tick >0 )
			return True


	def execute(self, action):
		if action == 'bid_da':
			self.bid_ad()
		elif action == 'negotiate_po':
			self.negotiate_po()
		elif action == 'give':
			self.charge_da()
		elif action == 'receive':
			self.receive_energy_po()


	def rebuildPlan(self):
		self.plan = []


	def reconsider(self):
		return True


	def deliberate(self):
		self.current_desires = []
		if(len(self.da_queue) > 0):
			if(self.energy_available == 0):
				self.current_desires.append('negotiate_po')

			elif(self.energy_available > 0):
				self.current_desires.append('bid_da')

		self.intention = self.current_desires[0]


	def buildPlan(self):
		self.plan = []
		if(self.intention == 'bid_da'):
			self.plan.append('bid_da')
			self.plan.append('give')

		if(self.intention == 'negotiate_po'):
			self.plan.append('negotiate_po')
			self.plan.append('receive')
			#self.plan.append('bid_da')
			#self.plan.append('give')


	def act(self):
		if len(self.plan) > 0 and self.succeededIntention() and not self.impossibleIntention():
			while len(self.plan)>0:
				action = self.plan.pop(0)
				if self.isPlanSound(action):
					self.execute(action)
				else:
					self.rebuildPlan()
				if self.reconsider():
					self.deliberate()
					
			self.buildPlan()	#not official but makes sense in this case (takeout)
		else:
			#print(self.plan)
			#print(self.intention)
			self.deliberate()
			self.buildPlan()
			#if len(self.plan ) == 0:
			#self.agentReactiveDecision()

	'''
	Actions
	'''
	'''
	o Turn On/Off charging CH
	o Calculate earnings
	o Communicate with DA
		▪ Message DA about the station
	o Communicate with PO
		▪ Message PO that needs more Units of Energy
		▪ Message PO the amount of energy spent
	o Communicate with CH
		▪ Message other CHs of waiting time
	'''
	def charge_da(self):
		da = self.da_queue[0]
		energy_da = self.bid_result
		self.
		da.give_energy(energy_da)

	def receive_energy_po(self):
		return

	def calculate_earnings(self):
		pass

	def message_drivers(self):
		pass

	def get_energy_for_step(self, energy):
		print('CH: Yay! I gots da energy! '+str(energy))
		pass

	def report_spent_energy(self):
		return 10

	#def forcast_energy_spendure(self): #for vehicles waiting
	def calculate_time_to_charge(self, total_energy_to_give, max_energy_per_tick):
		return math.ceil(total_energy_to_give / max_energy_per_tick)
	
	def get_time_of_wait(self):
		return

	def report_charge_time(self): #for each vehicle
		pass


	'''
	Bid with DA
	'''
	def bid_da(self):
		return


	'''
	Negotiate with PO
	'''
	def negotiate_po(self):
		return


	def compute_energyself(self):
		total = 0
		if(len(self.da_to_negotiate) > 0):
			for da in self.da_to_negotiate:
				total += da.get_energy_to_refill #TODO encontrar a função que recebe o valor que é preciso o carro ser carregado
		
		return total + (ch_passive_spend_energy * self.calculate_time_to_charge(total, max_per_tick)) #TODO receber o ch_passive_spend_energy e o max_per_tick de laguma maneira


	def get_energy_po(self):
		energy = self.compute_energy()
		po.ask_for_energy(energy, utility) #TODO encontrar esta função no PO


	def negotiate_power_receive(self):
		# CH with PO
		energy_needed = 0
		utility = 0
		return self.id, energy_needed, utility

	def negotiate_power_give(self):
		# CH with DA
		#meter DA a pedir o memso power
		pass



'''
Testing
'''
class test_da:
	def __init__(self, id, ch):
		self.id = id
		self.ch = ch
		pass

	def act(self):
		self.ch.add_da_to_queue(self)



class test_po:
	def __init__(self):
		pass



if __name__ == "__main__":
	po = test_po()
	ch = charger_handler(1, 1, "", 1, 1, po)

	da = test_da(1, ch)
	da.act()

	#for da in ch.da_queue:
	#	print(da.id)
	
	ch.act() # vai escolher o plan (entra no else do act())

	ch.act() # aqui ja tem o plan e vai executa-lo (entra no if do act())





