from math import factorial
from math import hypot
from random import random

from algorithm import Algorithm


################ NEW #################################
class GranularBeeman(Algorithm):
	"""docstring for Beeman"""
	def __init__(self, N, L, W, D, d_min, d_max, g, tf, dt, kT, kN, m):
		super(GranularBeeman, self).__init__()
		self.dt = dt
		self.particles = [False for i in xrange(0,N)]
		self.L = L
		self.W = W
		self.D = D
		self.d_max = d_max
		self.d_min = d_min
		self.kT = kT
		self.kN = kN
		cell_l_number = int(L/d_max)+1
		cell_w_number = int(W/d_max)+1
		
		for idd in xrange(0,N):
			print idd
			found = False
			particle = self.Particle(m = m, idd = idd, g = g, dt = dt, W = W, L = L, D = D, kT = kT, kN = kN, algorithm = self, cell_l_number = cell_l_number, cell_w_number = cell_w_number)
			self.particles[idd] = particle
			while not found:
				r = random() * (d_max - d_min) + d_min
				x = random() * (W - 2.0 * r) + r 
				y = random() * (L - 2.0 * r) + r
				particle.r = {"x" : x, "y": y}
				particle.rad = r
				particle.update_cell_coordinate()
				for other_particle in self.particles:
					if other_particle.id == particle.id:
						found = True
						break
					if hypot(particle.r["x"] - other_particle.r["x"], particle.r["y"] - other_particle.r["y"]) < (other_particle.rad + particle.rad):
						break

		
	def basic_loop(self):
		#import ipdb; ipdb.set_trace()
		self.ppp = False
		particles = filter(lambda p: p.activated,self.particles)
		for particle in particles:
			particle.update_r(self.dt)
		for particle in particles:
			particle.update_a_next(particles)
		for particle in particles:
			particle.update_v(self.dt)
		for particle in particles:
			particle.update_a()
		for particle in filter(lambda particle: not particle.activated or (particle.r["y"] < -self.L / 10.0), self.particles):
			found = False
			tries = 0
			while not found:
				if tries > 10:
					particle.activated = False
					break
				tries += 1 			
				r = particle.rad
				x = random() * (self.W - 2.0 * r) + r 
				y = self.L - r
				particle.r = {"x" : x, "y": y}
				particle.rad = r
				particle.update_cell_coordinate()
				found = True
				for other_particle in particles:
					if other_particle.id != particle.id:
						if hypot(particle.r["x"] - other_particle.r["x"], particle.r["y"] - other_particle.r["y"]) < (other_particle.rad + particle.rad):
							found = False
			if found:
				particle.activated = True
				if p.id not in map(lambda p: p.id, particles):
					particles.append(particle)


		#if self.ppp:
		#	with open('output/dataa.txt', 'w') as outfile:
		#		outfile.write(self.get_info(i = 0, L = self.L, D = self.D, W = self.W))

	################### GRANULAR GEAR
	class Particle(object):
		"""docstring for Particle"""
		def __init__(self, m, g, idd, dt, L, W, D, kN, kT, algorithm, cell_l_number, cell_w_number):
			super(self.__class__, self).__init__()
			self.activated = True
			self.m = m
			self.W = W
			self.L = L
			self.D = D
			self.kT = kT
			self.kN = kN
			self.g = g
			self.gx = 0.0
			self.v = {"x" : 0.0,"y" : 0.0}
			self.a = {"x" : 0.0,"y" : -g}
			self.a_prev = {"x" : 0.0,"y" : -g}
			self.id = idd
			self.dt = dt
			self.algorithm = algorithm
			self.cell_l_number = cell_l_number
			self.cell_w_number = cell_w_number

		def a_function(self,particles):
			Fx = 0.0
			Fy = 0.0
			#neighbours = self.getNeighbours(particles)
			particles = filter(lambda p: p.activated,particles)
					
			for other_particle in particles:
				if other_particle.id != self.id:
					
					dif_x = other_particle.r["x"] - self.r["x"]
					dif_y = other_particle.r["y"] - self.r["y"]
					dif_vx = self.v["x"] - other_particle.v["x"]
					dif_vy = self.v["y"] - other_particle.v["y"]
					distance = hypot(dif_x, dif_y)
					r_dif = other_particle.rad + self.rad - distance
					if r_dif > 0.0:
						#import ipdb; ipdb.set_trace()
						self.algorithm.ppp = True
						enx = dif_x / distance
						eny = dif_y / distance
						FN = - self.kN * r_dif
						#					     (t = -eny,enx); dot(t v)
						FT = - self.kT * r_dif * (-eny * dif_vx + enx * dif_vy)

						Fx += FN * enx + FT * (-eny)
						Fy += FN * eny + FT * enx
			if self.r["x"] < self.rad:
				#import ipdb; ipdb.set_trace() 
				r_dif = self.rad - self.r["x"]
				dif_vx = self.v["x"]
				dif_vy = self.v["y"]
				enx = -1.0
				eny = 0.0
				FN = - self.kN * r_dif
				FT = - self.kT * r_dif * (-eny * dif_vx + enx * dif_vy)
				Fx += FN * enx + FT * (-eny)
				Fy += FN * eny + FT * (enx)
			elif self.r["x"] > (self.W - self.rad):
				#import ipdb; ipdb.set_trace()
				r_dif = self.r["x"] - self.W + self.rad
				dif_vx = self.v["x"]
				dif_vy = self.v["y"]
				enx = 1.0
				eny = 0.0
				FN = - self.kN * r_dif
				FT = - self.kT * r_dif * (-eny * dif_vx + enx * dif_vy) 
				Fx += FN * enx + FT * (-eny)
				Fy += FN * eny + FT * enx
			if self.r["y"] < self.rad and (self.W-self.D)/2.0 < self.r["x"] < (self.W+self.D)/2.0 :
				pass
			elif self.r["y"] < self.rad:#import ipdb; ipdb.set_trace()
				r_dif = self.rad - self.r["y"]
				dif_vx = self.v["x"]
				dif_vy = self.v["y"]
				enx = 0.0
				eny = -1.0
				FN = - self.kN * r_dif
				FT = - self.kT * r_dif * (-eny * dif_vx + enx * dif_vy) 
				Fx += FN * enx + FT * (-eny)
				Fy += FN * eny + FT * enx
			elif self.r["y"] > (self.L - self.rad):
				#import ipdb; ipdb.set_trace()
				r_dif = self.r["y"] - self.L + self.rad
				dif_vx = self.v["x"]
				dif_vy = self.v["y"]
				enx = 0.0
				eny = 1.0
				FN = - self.kN * r_dif
				FT = - self.kT * r_dif * (-eny * dif_vx + enx * dif_vy) 
				Fx += FN * enx + FT * (-eny)
				Fy += FN * eny + FT * enx
			return {"x" : -self.gx + Fx/self.m,"y" : -self.g + Fy/self.m}

		def update_r(self, dt):
			self.r["x"] = self.r["x"] + self.v["x"] * dt + 2/3.0 * self.a["x"] * dt**2 - 1/6.0 * self.a_prev["x"] * dt**2
			self.r["y"] = self.r["y"] + self.v["y"] * dt + 2/3.0 * self.a["y"] * dt**2 - 1/6.0 * self.a_prev["y"] * dt**2
			self.update_cell_coordinate()
			
		def update_v(self, dt):
			self.v["x"] = self.v["x"] + 1/3.0 * self.a_next["x"] * dt + 5/6.0 * self.a["x"] * dt - 1/6.0 * self.a_prev["x"] * dt
			self.v["y"] = self.v["y"] + 1/3.0 * self.a_next["y"] * dt + 5/6.0 * self.a["y"] * dt - 1/6.0 * self.a_prev["y"] * dt
			
		def update_a(self):
			self.a_prev = self.a
			self.a = self.a_next

		def update_a_next(self,particles):
			self.a_next = self.a_function(particles)
		
		def getNeighbours(self,particles):
			return filter(lambda other_particle: self.id != other_particle.id and other_particle.activated and self.coordinate.in_range(other_particle.coordinate), particles)

		class CellCoordinate(object):
			"""docstring for CellCoordinate"""
			def __init__(self, x, y):
				super(self.__class__, self).__init__()
				self.x = x
				self.y = y

			def in_range(self,other_cell):
				return self.x == other_cell.x or self.x == other_cell.x -1 or self.x == other_cell.x + 1 and \
					self.y == other_cell.y or self.y == other_cell.y -1 or self.y == other_cell.y +1

			def equals(self,other_cell):
				return self.x == other_cell.x and self.y == other_cell.y

		def update_cell_coordinate(self):
			x_c = int(self.r["x"] * self.cell_w_number / self.W)
			y_c = int(self.r["y"] * self.cell_l_number / self.L)
			self.coordinate = self.CellCoordinate(x = x_c, y = y_c)

		def get_energy(self):
			if self.activated:
				return self.m * (((hypot(self.v["x"],self.v["y"]) ** 2) / 2))# + self.g * self.r["y"])
			return 0
	
	def get_energy_sum(self):
		return sum (map(lambda particle: particle.get_energy(), self.particles))

	def get_info(self, i, L, W, D):
		string = ""
		string += '\t' + str(len(self.particles)+4) + '\n'
		string += '\t' + str(i) + '\n'
		
		particles = filter(lambda p: p.activated,self.particles)
		for particle in particles:
			string += '\t' + str(particle.id) + '\t' + str(particle.r["x"]) + '\t' + str(particle.r["y"]) + '\t' + str(particle.rad) + '\t' + str(particle.v["x"]) + '\t' + str(particle.v["y"]) + '\t' + str(particle.a["x"]) + '\t' + str(particle.a["y"]) + '\t' + str(1) + '\t' + str(0) + '\t' + str(0) + '\n'
		string += '\t' + str(len(particles)) + '\t' + str(0) + '\t' + str(0) + '\t' + str(0.000000001) + '\t' + str(0) + '\t' + str(0) + '\t' + str(0) + '\t' + str(0) + '\t' + str(0) + '\t' + str(0) + '\t' + str(0) + '\n'
		string += '\t' + str(len(particles)+1) + '\t' + str(W) + '\t' + str(0) + '\t' + str(0.000000001) + '\t' + str(0) + '\t' + str(0) + '\t' + str(0) + '\t' + str(0) + '\t' + str(0) + '\t' + str(0) + '\t' + str(0) + '\n'
		string += '\t' + str(len(particles)+2) + '\t' + str(0) + '\t' + str(L) + '\t' + str(0.000000001) + '\t' + str(0) + '\t' + str(0) + '\t' + str(0) + '\t' + str(0) + '\t' + str(0) + '\t' + str(0) + '\t' + str(0) + '\n'
		string += '\t' + str(len(particles)+3) + '\t' + str(W) + '\t' + str(L) + '\t' + str(0.000000001) + '\t' + str(0) + '\t' + str(0) + '\t' + str(0) + '\t' + str(0) + '\t' + str(0) + '\t' + str(0) + '\t' + str(0) + '\n'
		#ipdb.set_trace()
		return string
			