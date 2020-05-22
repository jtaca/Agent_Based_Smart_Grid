import geographic_agent

class power_operative(geographic_agent.geographic_agent):

		def __init__(self,lat,lng, storage_available,simulation):
				geographic_agent.geographic_agent.__init__(self,lat,lng,'k', '$P$', 100,2)
				self.name = "power operative"
				self.acumulated_energy = 0
				self.storage_available = storage_available
				self.available_for_tick = 0
				self.simulation = simulation
				self.ch_list = []
				for i in self.simulation.agent_list:
					if i.name == "charger handler":
						self.ch_list.append(i)
				self.report_list =[]

		def act(self):

			pass

		def calculate_energy_used_in_tick(self):
			pass

		def redistribute_energy(self): 
			#should calculate how much per ch 
			#should output a vector
			pass

		def ask_for_spending_report(self):
			self.report_list =[]
			for ch in ch_list:
				report_list.append(ch.report_spent_energy())
			pass

		def give_power(self):

			#give power to ch
			pass 

		def recieve_energy(self, energy):
			print("PO give: "+ str( energy))
			self.available_for_tick = self.storage_available + energy
			#pass # current power = new + accumulated (form PO)

		def store_remaining_energy(self):
			pass

		#def request_energy(self):
		#	pass

