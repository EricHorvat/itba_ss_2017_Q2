from math import factorial
from math import hypot
from random import random

from algorithm import Algorithm

class GranularGear(Algorithm):
	"""docstring for Gear"""
	def __init__(self, N, L, W, D, d_min, d_max, g, tf, dt, kT, kN, m):
		super(GranularGear, self).__init__()
		self.dt = dt
		self.particles = [False for i in xrange(0,N)]
		self.L = L
		self.W = W
		self.D = D
		self.kT = kT
		self.kN = kN
		for idd in xrange(0,N):
			print idd
			found = False
			while not found:
				r = random() * (d_max - d_min) + d_min
				x = random() * (W - 2.0 * r) + r 
				y = random() * L
				particle = self.Particle(x = x, y = y, r = r, m = m, idd = idd, g = g, dt = dt, W = W, kT = kT, kN = kN)
				self.particles[idd] = particle
				for other_particle in self.particles:
					if other_particle.id == particle.id:
						found = True
						break
					if hypot(particle.r_corr[0]["x"] - other_particle.r_corr[0]["x"], particle.r_corr[0]["y"] - other_particle.r_corr[0]["y"]) < other_particle.rad + particle.rad:
						break
		

	def basic_loop(self):
		#import ipdb; ipdb.set_trace()
		for particle in self.particles:
			particle.update_predicted()
		for particle in self.particles:
			particle.r_corr[2] = particle.a_function(particles = self.particles, use_pred = True)
		for particle in self.particles:
			particle.update_corrected()

	class Particle(object):
		"""docstring for Particle"""
		def __init__(self, x, y, r, m, g, idd, dt, W, kN, kT):
			super(self.__class__, self).__init__()
			self.rad = r
			self.m = m
			self.W = W
			self.kT = kT
			self.kN = kN
			self.g = g
			self.r = {"x" : x,"y" : y}
			self.v = {"x" : 0.0,"y" : 0.0}
			self.a = {"x" : 0.0,"y" : -g}
			self.id = idd
			self.dt = dt
			self.r_pred = [{"x" : 0.0,"y" : 0.0} for i in xrange(1,7)]
			self.r_corr = self.get_initial_r_corr()
			self.alpha = [3/20.0,251/360.0,1.0,11/18.0,1/6.0,1/60.0]

		def a_function(self,particles, use_pred):
			#TODO CHECK, SET NEIGHTBOURS
			Fx = 0.0
			Fy = 0.0

			if use_pred:
				r = self.r_pred
			else:
				r = self.r_corr


			for other_particle in particles:
				if other_particle.id != self.id:
					other_particle_r = other_particle.r_pred if use_pred else other_particle.r_corr
					dif_x = other_particle_r[0]["x"] - r[0]["x"]
					dif_y = other_particle_r[0]["y"] - r[0]["y"]
					dif_vx = other_particle_r[1]["x"] - r[1]["x"]
					dif_vy = other_particle_r[1]["y"] - r[1]["y"]
					distance = hypot(dif_x, dif_y)
					r_dif = other_particle.rad + self.rad - distance
					if r_dif > 0.0:
						
						enx = dif_x / distance
						eny = dif_y / distance
						FN = - self.kN * r_dif
						#					(-eny,enx = t);dot(t r)
						FT = - self.kT * r_dif * (-eny * dif_vx + enx * dif_vy)

						Fx += FN * enx + FT * (-eny)
						Fy += FN * eny + FT * enx
			if r[0]["x"] < self.rad:
				import ipdb; ipdb.set_trace() 
				r_dif = self.rad - r[0]["x"]
				FN = - self.kN * r_dif
				FT = - self.kT * r_dif * (r[1]["y"] )
				Fx += -FN
				Fy += -FT
			elif r[0]["x"] > (self.W - self.rad):
				import ipdb; ipdb.set_trace()
				r_dif = r[0]["x"] - self.W + self.rad
				FN = - self.kN * r_dif
				FT = - self.kT * r_dif * (r[1]["y"])
				Fx += FN
				Fy += FT
			if r[0]["y"] < self.rad:
				import ipdb; ipdb.set_trace()
				r_dif = self.rad - r[0]["y"]
				FN = - self.kN * r_dif
				FT = - self.kT * r_dif * (r[1]["x"])
				Fx += FT
				Fy += -FN
			return {"x" : Fx/self.m,"y" : -self.g + Fy/self.m}
			
		def update_corrected(self):
			ax_diff = self.r_corr[2]["x"] - self.r_pred[2]["x"]
			ay_diff = self.r_corr[2]["y"] - self.r_pred[2]["y"]
			dt = self.dt
			x2_diff = ax_diff * dt ** 2 / factorial(2)
			y2_diff = ay_diff * dt ** 2 / factorial(2)
			for i in xrange(0,6):
		 		self.r_corr[i]["x"] = self.r_pred[i]["x"] + self.alpha[i] * x2_diff * factorial(i) / (dt**i)
		 		self.r_corr[i]["y"] = self.r_pred[i]["y"] + self.alpha[i] * y2_diff * factorial(i) / (dt**i)
			self.r = self.r_corr[0]
			self.v = self.r_corr[1]
			self.a = self.r_corr[2]

		def update_predicted(self):
			r = self.r_corr
			dt = self.dt
			for axis in ["x","y"]:
				self.r_pred[0][axis] =	r[0][axis] + \
										r[1][axis] * dt + \
										r[2][axis] * dt ** 2 / factorial(2) + \
										r[3][axis] * dt ** 3 / factorial(3) + \
										r[4][axis] * dt ** 4 / factorial(4) + \
										r[5][axis] * dt ** 5 / factorial(5)
				self.r_pred[1][axis] =	r[1][axis] + \
										r[2][axis] * dt + \
										r[3][axis] * dt ** 2 / factorial(2) + \
										r[4][axis] * dt ** 3 / factorial(3) + \
										r[5][axis] * dt ** 4 / factorial(4)
				self.r_pred[2][axis] =	r[2][axis] + \
										r[3][axis] * dt + \
										r[4][axis] * dt ** 2 / factorial(2) + \
										r[5][axis] * dt ** 3 / factorial(3)
				self.r_pred[3][axis] =	r[3][axis] + \
										r[4][axis] * dt + \
										r[5][axis] * dt ** 2 / factorial(2)
				self.r_pred[4][axis] =	r[4][axis] + \
								 		r[5][axis] * dt
				self.r_pred[5][axis] =	r[5][axis]

		def get_initial_r_corr(self):
			#a = self.a_function(particles)
			#next_x = self.x+self.vx*self.dt+ a["x"]/2.0*self.dt**2
			#next_y = self.y+self.vy*self.dt+ a["y"]/2.0*self.dt**2
			#next_vx = self.vx+a["x"]*self.dt
			#next_vy = self.vy+a["y"]*self.dt
			#dr = next_r - r
			#k_div_m = k/m
			#TODO EDIT
			return [self.r,
					self.v,
					self.a,
					{"x" : 0.0,"y" : 0.0},
					{"x" : 0.0,"y" : 0.0},
					{"x" : 0.0,"y" : 0.0}]
