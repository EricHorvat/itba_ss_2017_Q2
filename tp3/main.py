import json
import ipdb
import pprint
import colored_traceback
import sys
import os
import numpy
from math import floor
from math import cos
from math import sin
from math import tan
from math import atan2
from math import hypot
from math import pi
from math import sqrt
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import getopt
import random
import time
import copy

colored_traceback.add_hook()

def init():
	folders = ['output']
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
	print('usage:	python main.py [options]')
	print('-h --help:	print this screen')
	print('-c --config=:	configuration file')

def parse_arguments():
	arguments = {
		'config': './config/config.json',
	}
	try:
		opts, args = getopt.getopt(sys.argv[1:], 'hc:tn', ['help', 'config=', 'partition=', 'eta_step=', 'density_step='])
	
	except getopt.GetoptError as err:
		print str(err)  # will print something like "option -a not recognized"
		usage()
		sys.exit(2)
	
	for o, a in opts:
		if o in ('-h', '--help'):
			usage()
			sys.exit()
		elif o in ('-c', '--config'):
			arguments['config'] = a
		elif o in ('-p','--partition'):
			arguments['partition'] = int(a)
		elif o in ('--eta_step'):
			arguments['eta_step'] = int(a)
		elif o in ('--density_step'):
			arguments['density_step'] = int(a)
		else:
			assert False, 'unknown option `' + o + '`' 

	return arguments

class Particle(object):
	x = 0

	def __init__(self, x, y, vx, vy, r, m, color):
		super(Particle, self).__init__()
		self.x = x
		self.y = y
		self.vx = vx
		self.vy = vy
		self.r = r
		self.m = m
		self.color = color

def generate(N, L, r, v, m, r2, m2):
	
	x = random.random() * (L - 2 * r2) + r2
	y = random.random() * (L - 2 * r2) + r2
	particles = [Particle(x = x, y = y, vx = 0, vy = 0, r = r2, m = m2, color = "R")]
	for part in xrange(1, N + 1):
		print part
		x = random.random() * (L - 2 * r) + r
		y = random.random() * (L - 2 * r) + r
		v_rand = random.random() * 2 * v - v
		angle = random.random() * 2 * pi
		vx = cos(angle) * v_rand
		vy = sin(angle) * v_rand
		while reduce(lambda acumm, elem: (hypot(elem.x-x, elem.y-y) < r + elem.r) or acumm, particles, False):
			x = random.random() * L
			y = random.random() * L	

		print x, y
		particles.append(Particle(x = x, y = y, vx = vx, vy = vy, r = r, m = m, color = "B"))
	return particles

def get_info(particles, L, i):
	string = ""
	string += '\t' + str(len(particles)+4) + '\n'
	string += '\t' + str(i) + '\n'
	for particle in particles:
		string += '\t' + str(particle.x) + '\t' + str(particle.y) + '\t' + str(particle.r) + '\n'
	string += '\t' + str(0) + '\t' + str(0) + '\t' + str(0.00000001) + '\n'
	string += '\t' + str(L) + '\t' + str(0) + '\t' + str(0.00000001) + '\n'
	string += '\t' + str(0) + '\t' + str(L) + '\t' + str(0.00000001) + '\n'
	string += '\t' + str(L) + '\t' + str(L) + '\t' + str(0.00000001) + '\n'
	return string

VA = "va"
FILE = "file"

def save_file(file_string):
	with open('output/brownian.txt', 'w') as outfile:
		outfile.write(file_string)

def start(L, particles, iterations):
	i = 0

	x1 = 0
	x2 = L
	y1 = 0
	y2 = L

	file_string = get_info(particles = particles,L = L, i = i)
	import ipdb
	while i < iterations:
		print i
		#ipdb.set_trace()
	

		min_tc = False
		# 2
		for (index,particle) in enumerate(particles):
			
			if(particle.vx > 0):
				x_tc = (x2 - particle.r - particle.x)/ particle.vx
			elif(particle.vx < 0):
				x_tc = (x1 + particle.r - particle.x)/ particle.vx
			else:
				x_tc = float('inf')
			if(particle.vy > 0):
				y_tc = (y2 - particle.r - particle.y)/ particle.vy
			elif(particle.vy < 0):
				y_tc = (y1 + particle.r - particle.y)/ particle.vy
			else:
				y_tc = float('inf')
			
			min_tc = (x_tc,index,-1) if not min_tc or x_tc <= min_tc[0] else min_tc
			min_tc = (y_tc,index,-2) if y_tc <= min_tc[0] else min_tc

			for (other_index, other_particle) in enumerate(particles):
				if index < other_index:
					sigma = particle.r + other_particle.r
					dx = other_particle.x - particle.x
					dy = other_particle.y - particle.y
					dvx = other_particle.vx - particle.vx
					dvy = other_particle.vy - particle.vy 
					drdr = dx**2+dy**2 
					dvdv = dvx**2+dvy**2
					dvdr = dvx*dx + dvy*dy
					d = dvdr**2 - dvdv * (drdr - sigma**2)
					if d >=0 and dvdr < 0:
						tc =  - (dvdr + sqrt(d)) / dvdv
						min_tc = (tc,index,other_index) if tc <= min_tc[0] else min_tc
			print min_tc

		#ipdb.set_trace()

		tc = min_tc[0]
		collide_particle = particles[min_tc[1]]
		collide_element_index = min_tc[2]
		
		#3
		for particle in particles:
			particle.x = particle.x + particle.vx * tc
			particle.y = particle.y + particle.vy * tc 

		#4
		if collide_element_index == -2:
			collide_particle.vy = -collide_particle.vy
		elif collide_element_index == -1:
			collide_particle.vx = -collide_particle.vx
		else:
			collide_other_particle = particles[collide_element_index]
			sigma = collide_particle.r + collide_other_particle.r
			dx = collide_other_particle.x - collide_particle.x
			dy = collide_other_particle.y - collide_particle.y
			dvx = collide_other_particle.vx - collide_particle.vx
			dvy = collide_other_particle.vy - collide_particle.vy 
			dvdr = dvx*dx + dvy*dy
			J = 2 * collide_particle.m * collide_other_particle.m * dvdr / (sigma * (collide_particle.m + collide_other_particle.m) ) 
			Jx = J * dx / sigma
			Jy = J * dy / sigma

			collide_particle.vx = collide_particle.vx + Jx /collide_particle.m
			collide_particle.vy = collide_particle.vy + Jy /collide_particle.m
			collide_other_particle.vx = collide_other_particle.vx - Jx /collide_other_particle.m
			collide_other_particle.vy = collide_other_particle.vy - Jy /collide_other_particle.m
		file_string += get_info(particles = particles,L = L, i = i)

		i+=1

	save_file(file_string = file_string)
	

def main():

	arguments = parse_arguments()

	partition = arguments['partition'] if 'partition' in arguments else 0
	eta_step = arguments['eta_step'] if 'eta_step' in arguments else 0
	density_step = arguments['density_step'] if 'density_step' in arguments else 0
	
	init()

	with open(arguments['config']) as data_file:
		global data
		data = json.load(data_file)

	pprint.pprint(data)

	iterations = data['world']["interations"] if 'world' in data else data["iterations"]
	N = data['world']["N"] if 'world' in data else data["N"]

	L=0.5
	r=0.005
	r2=0.05
	m=0.1
	m2=100
	v = 0.1
	particles = data['particles'] if 'particles' in data else generate(N = N, L = L, r = r, v = v, m = m, r2 = r2, m2 = m2)



	density = N/(L**2)

	if eta_step > 0:
		for eta_summ in numpy.arange(0, eta+eta*eta_step/100, eta*eta_step/100.0):
			start(M = M, L = L, rc = rc, particles = copy.deepcopy(particles), eta = eta_summ, partition = partition, v = v, iterations = iterations, parameter="particle_number")
	elif density_step > 0:
		for density_summ in xrange(density_step,100+density_step, density_step):
			N_step = int(floor(N * density_summ/100.0))
			particles = generate(N = N_step, L = L, r = r, v = v)
			start(M = M, L = L, rc = rc, particles = particles, eta = eta, partition = partition, v = v, iterations = iterations, parameter="particle_number")
	else:
			start(L = L, particles = particles, iterations = iterations)



if __name__ == '__main__':
	main()