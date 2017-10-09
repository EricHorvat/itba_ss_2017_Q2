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
		for iid in xrange(0,N):
			found = False
			while not found:
				r = random() * (d_max - d_min) + d_min
				x = random() * (W - 2 * r) + r 
				y = random() * L/10.0 + L*9/10.0
				particle = Particle(x = x, y = y, r = r, idd = idd)
				particles[iid] = particle
				for other_particle in particles:
					if other_particle.id == particle.id:
						found = True
						break
					if hypot(particle.x - other_particle.x, particle.y - other_particle.y) < other_particle.r + particle.r:
						break
			
		## TODO EDIT
		self.r_corr = self.get_initial_r_corr(r = r, v = v, k = k, m = m)
		

	def basic_loop(self):
		#import ipdb; ipdb.set_trace()
		for particle in self.particles:
			particle.update_predicted()
			particle.r_corr[2] = particle.a_function(particles = self.particles, use_pred = True)
			particle.update_corrected()

	class Particle(object):
		"""docstring for Particle"""
		def __init__(self, x, y, r, idd):
			super(Particle, self).__init__()
			self.r = {"x" : x,"y" : y}
			self.v = {"x" : 0,"y" : 0}
			self.a = {"x" : 0,"y" : g}
			self.id = idd
			self.r_pred = [{"x" : 0,"y" : 0} for i in xrange(1,7)]
			self.alpha = [3/16.0,251/360.0,1.0,11/18.0,1/6.0,1/60.0]

		def a_function(self,particles, use_pred):
			#TODO DO, SET NEIGHTBOURS
			for other_particle in particles:
				if other_particle.id != self.id:
					pass

		def update_corrected(self):
			ax_diff = self.r_corr[2]["x"] - self.r_pred[2]["x"]
			ay_diff = self.r_corr[2]["y"] - self.r_pred[2]["y"]
			dt = self.dt
			x2_diff = ax_diff * dt ** 2 / factorial(2)
			y2_diff = ay_diff * dt ** 2 / factorial(2)
			for i in xrange(0,6):
		 		self.r_corr[i]["x"] = self.r_pred[i]["x"] + self.alpha[i]["x"] * x2_diff * factorial(i) / (dt**i)
		 		self.r_corr[i]["y"] = self.r_pred[i]["y"] + self.alpha[i]["y"] * y2_diff * factorial(i) / (dt**i)
			self.r = self.r_corr[0]
			self.v = self.r_corr[1]
			self.a = self.r_corr[2]

		def update_predicted(self):
			r = self.r_corr
			dt = self.dt
			for axis in ["x","y"]
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

		def get_initial_r_corr(self,particles):
			a = self.a_function(particles)
			next_x = self.x+self.vx*self.dt+ a["x"]/2.0*self.dt**2
			next_y = self.y+self.vy*self.dt+ a["y"]/2.0*self.dt**2
			next_vx = self.vx+a["x"]*self.dt
			next_vy = self.vy+a["y"]*self.dt
			dr = next_r - r
			k_div_m = k/m
			#TODO EDIT
			return [{"x" : next_x,"y" : next_y},
					{"x" : next_vx,"y" : next_vy},
					- k_div_m * dr, 
					- k_div_m * v, 
					k_div_m ** 2 * dr, 
					k_div_m ** 2 * v]
