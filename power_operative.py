import geographic_agent



class power_operative(geographic_agent.geographic_agent):

		def __init__(self,lat,lng, storage_available,simulation):
				geographic_agent.geographic_agent.__init__(self,lat,lng,'k', "D", 40,2)
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
				self.report_list_negotiated =[]
				self.gave = False

				#deliberative
				self.desires = ['negotiate', 'give', 'store']
				self.actions = ['negotiate', 'give', 'store','get_reports', 'redistribute'] #recieve could be an action?
				self.plan = []
				self.intention = 'store'
				self.current_desires =[]


		def updateBeliefs(self):
			self.ask_for_spending_report()
			pass

		def succeededIntention(self):
			if self.intention == 'negotiate':
				return len(self.report_list) > 0#True #change to got good price
			elif self.intention == 'give':
				return self.available_for_tick > 0 or self.acumulated_energy > 0
			elif self.intention == 'store':
				return (self.acumulated_energy < self.storage_available )
			else:
				return False
			pass

		def impossibleIntention(self):
			#for now nothing is impossible
			return False
			pass
		def isPlanSound(self,action):
			if action == 'negotiate':
				return len(self.ch_list) >= 1 or len(self.report_list) >= 1 #True 
			elif action == 'give':
				return self.available_for_tick > 0 or self.acumulated_energy > 0
			elif action == 'store':
				return (self.acumulated_energy < self.storage_available and self.available_for_tick >0 )
			elif action == 'get_reports':
				return len(self.ch_list) > 0 
			elif action == 'redistribute':
				return 	len(self.ch_list) >= 1 or len(self.report_list) >= 1 
			pass
		def execute(self, action):
			if action == 'negotiate':
				self.negotiate()
			elif action == 'give':
				self.give_power()
			elif action == 'store':
				self.store_remaining_energy()
			elif action == 'get_reports':
				self.ask_for_spending_report() 
			elif action == 'redistribute':
				self.redistribute_energy()
			pass
		def rebuildPlan(self):
			self.plan =[]
			pass
		def reconsider(self):
			return True
			pass
		def deliberate(self):
			
			self.current_desires =[]
			if self.available_for_tick > 0:
				self.current_desires.append('store')

			if len(self.report_list_negotiated)>0 and not self.gave: 
				self.current_desires.append('give')

			if len(self.report_list) > 0 and len(self.report_list_negotiated)==0  :
				self.current_desires.append('negotiate')
			
			self.intention = self.current_desires[-1]
			#if self.intention == 'store':

			pass
		def buildPlan(self):
			self.plan = []
			if self.intention == 'negotiate':
				#for i in range(self.simulation.steps-1):
				self.plan.append('negotiate')
				self.plan.append('redistribute')
				self.plan.append('give')
				self.plan.append('store')
				#self.plan.append('negotiate')
			elif self.intention == 'give':
				self.plan.append('redistribute')
				self.plan.append('give')
				#self.give_power()
			elif self.intention == 'store':
				self.plan.append('store')
				#self.store_remaining_energy()
			pass
		def agentReactiveDecision(self):
			self.store_remaining_energy()
			print('PO: i gonne ractive')
			pass


		def act(self):
			self.updateBeliefs()
		
			if len(self.plan)>0 and self.succeededIntention() and not self.impossibleIntention():
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
				self.agentReactiveDecision()
			

		def negotiate(self):
			sum_power = 0
			for i in self.report_list:
				sum_power += i[3]
				#agreed = False
				#while not agreed:
			if  sum_power <= self.available_for_tick:
				for agent in self.ch_list:
					if agent.id == i[0] and len(agent.da_queue) > 0:
				
						self.report_list_negotiated.append(i)
					
				#self.report_list_negotiated.append(self.report_list[1])
			else:
				redistribution = self.redistribute_energy()
				#for i in sorted_by_utility:
				#for ch in self.ch_list
				#	ch, energy_wanted, utility= ch.negotiate_power_receive(energy_wanted)

			#print(self.report_list)
			#####################For now its the same
			#print(self.report_list_negotiated)
			self.gave = False
			pass

		def calculate_energy_used_in_tick(self):
			#record energy used in tick and energy available along the simulation
			pass

		def redistribute_energy(self): 
			#should calculate how much per ch 
			#should output a vector
			print('PO: Im redistributing people! Tighten da belt!')
			
			self.sorted_by_utility = sorted(self.report_list, key=lambda tup: tup[1])
			for i in self.sorted_by_utility:
				if self.available_for_tick >= i[3]:
					for agent in self.ch_list:

						if agent.id == i[0] and len(agent.da_queue) > 0:
							self.report_list_negotiated.append(i)
					#self.report_list_negotiated.append(i)

			if len(self.report_list_negotiated) < 1:
				aux = [0,0,0,0,0]
				count = 0
				max = 0
				min = float("inf")
				maxid = 0
				ch_credible = False
				for i in self.sorted_by_utility:
					if agent.id == i[0] and len(agent.da_queue) > 0 and max < i[1] and min > i[4]:
							self.report_list_negotiated.append(i)
							maxid = i[0]
							max = i[1]
							min = i[4]
							ch_credible = True

				if ch_credible:
					for i in self.sorted_by_utility[maxid]:
						aux[count]= i
						count+=1
					
					aux[3] = self.available_for_tick
					self.report_list_negotiated.append(aux)


			pass

		def ask_for_spending_report(self):
			self.report_list =[]
			for ch in self.ch_list:
				self.report_list.append(ch.report_spent_energy())
			#print(self.report_list)
			pass

		def give_power(self):
			for proposal in self.report_list_negotiated:
				print(proposal)
				if self.available_for_tick >= proposal[3]:

					self.ch_list[proposal[0]].get_energy_for_step(proposal[3])
					self.available_for_tick -= proposal[3]
					print("PO: gave "+ str(proposal[3])+" to CH "+str(proposal[0]))

				elif self.acumulated_energy >= proposal[1]:
					self.ch_list[proposal[0]].get_energy_for_step(proposal[1])
					self.acumulated_energy -= proposal[1]
					print("PO: gots like: "+ str(self.available_for_tick))

				else :
					print("PO: gots no power brah..")
					#self.ch_list[index].get_energy_for_step(self.report_list_negotiated[index])

			self.gave = True
			self.report_list_negotiated = []
				#print("PO: give: "+ str( energy))

			#give power to ch
			pass 

		def recieve_energy(self, energy):

			if self.acumulated_energy > 0:
				self.simulation.map1.add_points_to_print((self.get_longitude(),self.get_latitude()),'m','P',20)
			if energy > 0:
				self.simulation.map1.add_points_to_print((self.get_longitude(),self.get_latitude()),'c','P',20)
			
			

			self.available_for_tick =  energy +self.acumulated_energy

			self.simulation.po_power.append(self.available_for_tick)
			#self.intention = 'give'
			self.act()
			#pass # current power = new + accumulated (form PO)

		def store_remaining_energy(self):
			self.acumulated_energy = min(self.available_for_tick,self.storage_available)
			print('PO: stored: '+ str(self.acumulated_energy))

			pass

		#def request_energy(self):
		#	pass

