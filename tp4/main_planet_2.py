import json
import ipdb
import pprint
import colored_traceback
import sys
import os
import getopt
import matplotlib.pyplot as plt
import numpy as np
from math import exp
from math import pi
from math import cos
from math import sin
from math import atan2
from math import hypot
from mpl_toolkits.mplot3d import Axes3D

colored_traceback.add_hook()

G = 6.693e-11

def frange(start, stop = False, step = 0.1):    
	if not stop:
		stop = start
		start = 0.0
	x = start
	while x < stop:
		yield x
		x += step

def init():
	folders = ['output_planet']
	for folder in folders:
		folder_path = os.path.join('.', folder)
		if not os.path.exists(folder_path):
			os.makedirs(folder_path)

	for folder in folders:
		folder_path = os.path.join('.', folder)
		for file in os.listdir(folder):
			file_path = os.path.join(folder, file)
			if os.path.isfile(file_path):
				os.remove(file_path)

def usage():
	print('usage:	python main.py')

def parse_arguments():
	arguments = {
		'config': './config_planet/config.json',
	}
	try:
		opts, args = getopt.getopt(sys.argv[1:], 'hc:tn', ['help','config'])
	
	except getopt.GetoptError as err:
		print str(err)  # will print something like "option -a not recognized"
		usage()
		sys.exit(2)
	
	for o, a in opts:
		if o in ('-h', '--help'):
			usage()
			sys.exit()
		else:
			assert False, 'unknown option `' + o + '`' 

	return arguments

def start(planets, ship):
	distance = []
	min_distance_dic = {}
	min_t_dic = {}

	angles = []
	velocities = []
	times = []
	distances = []


	#for angle in xrange(90,270):
	for angle in frange(0.0,180.0,10.0):
		print angle

		min_distance_ang_dic = {}
		min_t_ang_dic = {}
		for v in frange(1.0e4, 8.0e4, 1.0e3):
			print v
			min_distance = False
			#TODO TODOOOOOO AND V 
			planet_system = PlanetSystem(planets = planets, dt = dt)
			info = planet_system.get_info(0)
			planet_system.launch_ship(ship,delta_angle = angle *2*pi/360.0 , v = v)
			min_distance = min_distance if min_distance else (planet_system.get_ship_distance_to_mars(),0,v)
			for index in xrange(1,int(tf/dt)+1):

				t = index * dt

				planet_system.loop()

				
				#import ipdb; ipdb.set_trace()
									
				
				if t % (dt2) == 0:
					info += planet_system.get_info(index)
				new_distance = (planet_system.get_ship_distance_to_mars(),t,v)
				if min_distance[0] > new_distance[0]:
					min_distance = new_distance
					min_distance_ang_dic[v] = min_distance[0]
					min_t_ang_dic[v] = t

			angles.append(angle)
			velocities.append(v)
			times.append(min_distance[1])
			distances.append(min_distance[0])

		min_distance_dic[angle] = min_distance_ang_dic
		min_t_dic[angle] = min_t_ang_dic

		with open('output_planet/planet_system' + str(angle) + '.txt', 'w') as outfile:
			outfile.write(info)

	with open('output_planet/data.txt', 'w') as outfile:
		outfile.write(str(distance))

	with open('output_planet/datat.txt', 'w') as outfile:
		for i in range(len(angles)):
			outfile.write(str(angles[i]) + '\t' + str(velocities[i]) + '\t' + str(times[i]) + '\n')

	with open('output_planet/datad.txt', 'w') as outfile:
		for i in range(len(angles)):
			outfile.write(str(angles[i]) + '\t' + str(velocities[i]) + '\t' + str(distances[i]) + '\n')

	# print min_t_dic
	# print min_distance_dic

	# plot_surface([angles, velocities, times], 'times')
	# plot_surface([angles, velocities, distances], 'distances')

	# plot(min_t_dic, min_distance_dic)

def plot_surface(surface, f):
	fig = plt.figure()
	ax = fig.add_subplot(111, projection='3d')
	legends = ['Terreno Objetivo']
	ax.scatter(surface[0], surface[1], surface[2], c="y")
	plt.legend(legends)
	for angle in range(0, 181, 30):
		ax.view_init(30, angle)
		plt.savefig('terrain' + f + '-angle' + str(angle) + '.png')

	plt.close()

def plot(t_dic, distance_dic):
	

	#old from particle
	legends = ['Analitic','Velvet','Beeman','Gear']
	plt.plot(xrange(len(analitic_array)), analitic_array)
	plt.plot(xrange(len(analitic_array)), verlet_array)
	plt.plot(xrange(len(analitic_array)), beeman_array)
	plt.plot(xrange(len(analitic_array)), gear_array)
	plt.legend(legends)
	plt.xlabel('t')
	plt.ylabel('Y')
	_max = 1.0
	_min = -1.0
	_delta = (_max - _min) / 15
	_delta = 0.01 if _delta == 0 else _delta
	plt.yticks(np.arange(_min - _delta, _max + _delta, _delta))
	plt.savefig(os.path.join(os.getcwd(),"output_particle/i.png"))
	plt.close()
	#Correct last 1000 iteration
	plt.plot(xrange(len(analitic_array))[-1000], analitic_array[-1000])
	plt.plot(xrange(len(analitic_array))[-1000], verlet_array[-1000])
	plt.plot(xrange(len(analitic_array))[-1000], beeman_array[-1000])
	plt.plot(xrange(len(analitic_array))[-1000], gear_array[-1000])
	plt.legend(legends)
	plt.xlabel('t')
	plt.ylabel('Y')
	_max = 1.0
	_min = -1.0
	_delta = (_max - _min) / 15
	_delta = 0.01 if _delta == 0 else _delta
	plt.yticks(np.arange(_min - _delta, _max + _delta, _delta))
	plt.savefig(os.path.join(os.getcwd(),"output_particle/i2.png"))
	plt.close()

def main():

	arguments = parse_arguments()

	init()

	with open(arguments['config']) as data_file:
		global data
		data = json.load(data_file)

	pprint.pprint(data)

	global tf,dt,dt2

	planets = data["planets"] 
	ship = data["ship"] 
	tf = data["tf"] * 2.5
	dt = data["dt"]
	dt2 = data["dt2"]
	
	start(planets = planets, ship = ship)

class PlanetSystem(object):
	
	def __init__(self, planets, dt):
		super(PlanetSystem, self).__init__()
		self.planets = map(lambda elem: self.Planet(x = planets[elem]["x"],
												y = planets[elem]["y"],
												vx = planets[elem]["vx"],
												vy = planets[elem]["vy"],
												r = planets[elem]["r"],
												m = planets[elem]["m"],
												R = planets[elem]["R"],
												GG = planets[elem]["G"],
												B = planets[elem]["B"],
												name = elem),planets)

		for planet in self.planets:
			dic = self.a_function(planet)
			planet.ax = dic['ax']
			planet.ay = dic['ay']

		for planet in self.planets:
			planet.calculate_prev_position(dt = dt)

		for planet in self.planets:

			dic = self.a_function(planet)

			planet.x = planet.x_next
			planet.y = planet.y_next
			planet.ax_prev = dic['ax']
			planet.ay_prev = dic['ay']

		self.dt = dt

	class Planet(object):

		def __repr__(self):
			return str(self.name) + ": x = " + str(self.x) + ", y = " + str(self.y) + ", vx = " + str(self.vx) + ", vy = " + str(self.vy) + ", ax = " + str(self.ax) + ", ay = " + str(self.ay)

		def __init__(self, x, y, vx, vy, m, r, name, R, GG, B):
			super(self.__class__, self).__init__()
			self.x = x
			self.y = y
			self.vx = vx
			self.vy = vy
			self.m = m
			self.r = r
			self.R = R
			self.GG = GG
			self.B = B
			self.name = name

		#def calculate_next_position(self, dt):
		#	self.x = self.x + self.vx * dt + self.ax / 2.0 * dt **2
		#	self.y = self.y + self.vy * dt + self.ay / 2.0 * dt **2
		#	self.vx = self.vx + self.ax * dt
		#	self.vy = self.vy + self.ay * dt

		def calculate_prev_position(self, dt):
			self.x_next = self.x
			self.y_next = self.y
			self.x = self.x - self.vx * dt - self.ax / 2.0 * dt **2
			self.y = self.y - self.vy * dt - self.ay / 2.0 * dt **2
		
		def update_r(self, dt):
			self.x = self.x + self.vx * dt + 2/3.0 * self.ax * dt**2 - 1/6.0 * self.ax_prev * dt**2
			self.y = self.y + self.vy * dt + 2/3.0 * self.ay * dt**2 - 1/6.0 * self.ay_prev * dt**2

		def update_v(self, dt):
			self.vx = self.vx + 1/3.0 * self.ax_next * dt + 5/6.0 * self.ax * dt - 1/6.0 * self.ax_prev * dt
			self.vy = self.vy + 1/3.0 * self.ay_next * dt + 5/6.0 * self.ay * dt - 1/6.0 * self.ay_prev * dt

		def update_a(self):

			self.ax_prev = self.ax
			self.ay_prev = self.ay
			self.ax = self.ax_next
			self.ay = self.ay_next

	def a_function(self,planet):
		ax = 0
		ay = 0
		for other_planet in self.planets:
			if other_planet.name != planet.name:
				dif_x = other_planet.x - planet.x
				dif_y = other_planet.y - planet.y
				# CHANGE HERE NOT MODIFY????
				angle = atan2(dif_y,dif_x) 
				d_dif_x= dif_x - (other_planet.r + planet.r) * cos(angle)
				d_dif_y= dif_y - (other_planet.r + planet.r) * sin(angle)
				a_module = G * other_planet.m / (hypot(dif_y,dif_x)**2)
				#ipdb.set_trace()
				ax += cos(angle) * a_module #* dif_x / hypot(dif_y,dif_x)
				ay += sin(angle) * a_module #? -> revisar, es e * dif_y / hypot(dif_y,dif_x)
				#ax += a_module * dif_x / hypot(dif_y,dif_x)
				#ay += a_module * dif_y / hypot(dif_y,dif_x)
		return {'ax' : ax, 'ay' : ay}		

	def update_r(self):
		for planet in self.planets:
			planet.update_r(dt = self.dt)

	def get_a_next(self):
		for planet in self.planets:
			dic = self.a_function(planet)
			planet.ax_next = dic["ax"]
			planet.ay_next = dic["ay"]

	def update_v(self):
		for planet in self.planets:
			planet.update_v(dt = self.dt)

	def update_a(self):
		for planet in self.planets:
			planet.update_a()

	def loop(self):
		#print self.planets
		#ipdb.set_trace()
		self.update_r()
		self.get_a_next()
		self.update_v()
		self.update_a()

	def ship_launched(self):
		return len(filter(lambda planet: planet.name == "ship", self.planets)) > 0

	def get_ship_distance_to_mars(self):
		mars = filter(lambda planet: planet.name == "mars", self.planets)[0]
		ship = filter(lambda planet: planet.name == "ship", self.planets)[0]
		return hypot(mars.x - ship.x, mars.y - ship.y)

	def launch_ship(self, ship_dic,delta_angle,v):
		earth = filter(lambda planet: planet.name == "earth", self.planets)[0]
		sun = filter(lambda planet: planet.name == "sun", self.planets)[0]
		dif_x = sun.x - earth.x
		dif_y = sun.y - earth.y
		angle = atan2(dif_y,dif_x)
		v_angle = atan2(earth.vy,earth.vx) + delta_angle
		ex = earth.x / hypot(earth.y,earth.x)
		ey = earth.y / hypot(earth.y,earth.x)
		r = ship_dic["rad"]
		x = earth.x + ex * (ship_dic["r"] + earth.r)
		y = earth.y + ey * (ship_dic["r"] + earth.r)
		vx = earth.vx + ( ship_dic["v_orb"] + v) * cos(v_angle)
		vy = earth.vy + ( ship_dic["v_orb"] + v) * sin(v_angle)
		m = ship_dic["m"]
		R = ship_dic["R"]
		GG = ship_dic["G"]
		B = ship_dic["B"]
		name = "ship"
		ship = self.Planet(x = x, y = y, vx = vx, vy = vy, m = m, r = r, name = name, R = R, GG = GG, B = B)
		dic = self.a_function(ship)
		ship.ax = dic["ax"]
		ship.ay = dic["ay"]
		self.planets.append(ship)

		for planet in self.planets:
			planet.calculate_prev_position(dt = dt)

		
		for planet in self.planets:
			if planet.name == "ship":
				dic = self.a_function(planet)
				planet.ax_prev = dic['ax']
				planet.ay_prev = dic['ay']

		for planet in self.planets:
			planet.x = planet.x_next
			planet.y = planet.y_next

	def get_info(self,i):

		string = ""
		string += '\t' + str(len(self.planets)) + '\n'
		string += '\t' + str(i) + '\n'
		
		for planet in self.planets:
			if planet.name =="sun":
				#string += '\t' +  str(planet.x) + '\t' + str(planet.y) + '\t' + str(planet.r*100) + '\t' + str(planet.R) + '\t' + str(planet.GG) + '\t' + str(planet.B) + '\n' #+ str(particle["angle"]%360) + '\n'
				string += '\t' +  str(planet.x) + '\t' + str(planet.y) + '\t' + str(planet.r*50) + '\t' + str(planet.R) + '\t' + str(planet.GG) + '\t' + str(planet.B) + '\n' #+ str(particle["angle"]%360) + '\n'
			elif planet.name =="ship":
				earth = filter(lambda planet: planet.name == "earth", self.planets)[0]
				mars = filter(lambda planet: planet.name == "mars", self.planets)[0]
				#string += '\t' +  str(planet.x) + '\t' + str(planet.y) + '\t' + str(planet.r*100) + '\t' + str(planet.R) + '\t' + str(planet.GG) + '\t' + str(planet.B) + '\n' #+ str(particle["angle"]%360) + '\n'
				string += '\t' +  str(planet.x) + '\t' + str(planet.y) + '\t' + str(earth.r*500) + '\t' + str(planet.R) + '\t' + str(planet.GG) + '\t' + str(planet.B) + '\n' #+ str(particle["angle"]%360) + '\n'
			else:				
				#string += '\t' +  str(planet.x) + '\t' + str(planet.y) + '\t' + str(planet.r*100) + '\t' + str(planet.R) + '\t' + str(planet.GG) + '\t' + str(planet.B) + '\n' #+ str(particle["angle"]%360) + '\n'
				string += '\t' +  str(planet.x) + '\t' + str(planet.y) + '\t' + str(planet.r*2500) + '\t' + str(planet.R) + '\t' + str(planet.GG) + '\t' + str(planet.B) + '\n' #+ str(particle["angle"]%360) + '\n'
		#string += '\t' + str(0) + '\t' + str(0) + '\t' + str(0.00000001) + '\t' + str(0) + '\n'
		#string += '\t' + str(L) + '\t' + str(0) + '\t' + str(0.00000001) + '\t' + str(0) + '\n'
		#string += '\t' + str(0) + '\t' + str(L) + '\t' + str(0.00000001) + '\t' + str(0) + '\n'
		#string += '\t' + str(L) + '\t' + str(L) + '\t' + str(0.00000001) + '\t' + str(0) + '\n'
		#ipdb.set_trace()
		return string


if __name__ == '__main__':
	main()