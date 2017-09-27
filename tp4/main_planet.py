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
from math import cos
from math import sin
from math import atan2
from math import hypot

colored_traceback.add_hook()

G = 6.693e-11

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
		opts, args = getopt.getopt(sys.argv[1:], 'hc:tn', ['help'])
	
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

def start(planets):
	planet_system = PlanetSystem(planets = planets, dt = dt)
	info = ""
	for index in xrange(1,int(tf/dt)+1):
		t = index * dt
		#import ipdb; ipdb.set_trace()
		planet_system.loop()
		if index % (dt *1) == 0:
			info += planet_system.get_info(index)

	with open('output_planet/data.txt', 'w') as outfile:
		outfile.write(info)

def plot(analitic_array, verlet_array, beeman_array, gear_array):
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

	global tf,dt

	planets = data["planets"] 
	tf = data["tf"]
	dt = data["dt"]
	
	start(planets = planets)


class PlanetSystem(object):
	
	def __init__(self, planets, dt):
		super(PlanetSystem, self).__init__()
		self.planets = map(lambda elem: self.Planet(x = planets[elem]["x"],
												y = planets[elem]["y"],
												vx = planets[elem]["vx"],
												vy = planets[elem]["vy"],
												r = planets[elem]["r"],
												m = planets[elem]["m"],
												name = elem),planets)

		for planet in self.planets:
			(ax, ay) = self.a_function(planet)
			planet.ax = ax
			planet.ay = ay

		for planet in self.planets:
			planet.calculate_next_position(dt = dt)

		for planet in self.planets:
			ax = planet.ax
			ay = planet.ay

			(ax_next, ay_next) = self.a_function(planet)

			planet.ax_prev = ax
			planet.ay_prev = ay
			planet.ax = ax_next
			planet.ay = ay_next

		self.dt = dt

	class Planet(object):

		def __init__(self, x, y, vx, vy, m, r, name):
			super(self.__class__, self).__init__()
			self.x = x
			self.y = y
			self.vx = vx
			self.vy = vy
			self.m = m
			self.r = r
			self.name = name

		def calculate_next_position(self, dt):
			self.x = self.x + self.vx * dt + self.ax / 2 * dt **2
			self.y = self.y + self.vy * dt + self.ay / 2 * dt **2
			self.vx = self.vx + self.ax * dt
			self.vy = self.vy + self.ay * dt

		def update_r(self, dt):
			self.x = self.x + self.vx * dt + 2/3.0* self.ax * dt**2 - 1/6.0 * self.ax_prev * dt**2
			self.y = self.y + self.vy * dt + 2/3.0* self.ay * dt**2 - 1/6.0 * self.ay_prev * dt**2

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
				#d_dif_x= dif_x - (other_planet["r"] + planet["r"]) * cos(angle)
				#d_dif_y= dif_y - (other_planet["r"] + planet["r"]) * sin(angle)
				a_module = G * other_planet.m / (hypot(dif_y,dif_x)**2)
				#ipdb.set_trace()
				ax += cos(angle) * a_module #* dif_x / hypot(dif_y,dif_x)
				ay += sin(angle) * a_module #? -> revisar, es e * dif_y / hypot(dif_y,dif_x)
		return (ax,ay)		

	def update_r(self):
		for planet in self.planets:
			planet.update_r(dt = self.dt)

	def get_a_next(self):
		for planet in self.planets:
			(ax_next, ay_next) = self.a_function(planet)
			planet.ax_next = ax_next
			planet.ay_next = ay_next

	def update_v(self):
		for planet in self.planets:
			planet.update_v(dt = self.dt)

	def update_a(self):
		for planet in self.planets:
			planet.update_a()

	def loop(self):
		self.update_r()
		self.get_a_next()
		self.update_v()
		self.update_a()

	def get_info(self,i):

		string = ""
		string += '\t' + str(len(self.planets)) + '\n'
		string += '\t' + str(i) + '\n'
		for planet in self.planets:
			if planet.name =="sun":
				string += '\t' +  str(planet.x) + '\t' + str(planet.y) + '\t' + str(planet.r*10) + '\n' #+ str(particle["angle"]%360) + '\n'
			else:				
				string += '\t' +  str(planet.x) + '\t' + str(planet.y) + '\t' + str(planet.r*1000) + '\n' #+ str(particle["angle"]%360) + '\n'
		#string += '\t' + str(0) + '\t' + str(0) + '\t' + str(0.00000001) + '\t' + str(0) + '\n'
		#string += '\t' + str(L) + '\t' + str(0) + '\t' + str(0.00000001) + '\t' + str(0) + '\n'
		#string += '\t' + str(0) + '\t' + str(L) + '\t' + str(0.00000001) + '\t' + str(0) + '\n'
		#string += '\t' + str(L) + '\t' + str(L) + '\t' + str(0.00000001) + '\t' + str(0) + '\n'
		print string
		#ipdb.set_trace()
		return string


if __name__ == '__main__':
	main()