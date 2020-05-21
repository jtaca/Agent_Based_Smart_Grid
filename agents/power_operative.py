import agents.geographic_agent

class power_operative(agents.geographic_agent.geographic_agent):

		def __init__(self,lat,lng, storage_available):
				agents.geographic_agent.geographic_agent.__init__(self,lat,lng)
				self.name = "power operative"
				self.acumulated_energy = 0
				self.storage_available = storage_available

		def act(self):
			pass

		def calculate_energy_used_in_tick(self):
			pass

		def redistribute_energy(self): 
			#should calculate how much per ch 
			#should output a vector
			pass

		def ask_for_spending_report(self):
			pass

		def give_power(self):
			#recieve power for ch
			pass 

		def recieve_energy(self):
			pass # current power = new + accumulated (form PO)

		def store_energy(self):
			pass

		def request_energy(self):
			pass

