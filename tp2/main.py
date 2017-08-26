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
	print('-b --border:	The distance is calculated if the border are traspasable')

def parse_arguments():
	arguments = {
		'config': './config/config.json',
	}
	try:
		opts, args = getopt.getopt(sys.argv[1:], 'hc:tn', ['help', 'config=', 'border'])
	
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
		elif o in ('-b','--border'):
			arguments['border_control'] = True
		else:
			assert False, 'unknown option `' + o + '`' 

	return arguments

def get_neighbours(field, particle, rc, M, L):
	possible_neighbours = []
	x = particle["x"]
	y = particle["y"]
	x_c = int(floor(x * M / L))
	y_c = int(floor(y * M / L))
	xm1 = (x_c - 1) % M
	xp1 = (x_c + 1) % M
	ym1 = (y_c - 1) % M
	yp1 = (y_c + 1) % M
	x2py2 = x ** 2 + y ** 2

	x_a = [(x_c - i) % M for i in [-1,0,1]]
	y_a = [(y_c - i) % M for i in [-1,0,1]]
	for xx in x_a:
		for yy in y_a:
			possible_neighbours.extend(field[xx][yy])  
	#possible_neighbours.extend(field[xm1][y_c]) 
	#possible_neighbours.extend(field[xm1][yp1]) 
	#possible_neighbours.extend(field[x_c][ym1]) if border_control or ym1 >= 0  else noop()
	#possible_neighbours.extend(field[x_c][y_c]) 
	#possible_neighbours.extend(field[x_c][yp1]) if border_control or ym1 < M  else noop()
	#possible_neighbours.extend(field[xp1][ym1]) if border_control or (xp1 < M and ym1 >= 0) else noop()
	#possible_neighbours.extend(field[xp1][y_c]) if border_control or xp1 < M  else noop()
	#possible_neighbours.extend(field[xp1][yp1]) if border_control or (xp1 < M and yp1 < M) else noop()

	neighbours = filter(lambda part: ( 
		(L - abs(part["x"]-x))**2+(L-abs(part["y"]-y))**2 < (rc)**2
		or 
		(part["x"]-x)**2+(L-abs(part["y"]-y))**2 < (rc)**2
		or 
		(L - abs(part["x"]-x))**2+(part["y"]-y)**2 < (rc)**2
		or
		(part["x"]-x)**2+(part["y"]-y)**2 < (rc)**2
		), possible_neighbours)

	return neighbours

def get_color(angle):
	angle = (angle * 360 / (2 * pi))%360
	R=0
	G=0
	B=0
	if 0 <= angle < 180:
		R = 255
	if 120 <= angle < 300:
		G = 255
	if 240 <= angle < 360 or 0 <= angle < 60:
		B = 255
	return {"R":int(R), "G":int(G), "B":int(B)}


def get_field(M, L, in_particles = []):
	
	field = {} 
	for x in xrange(0, M):
		field_x = {} 
		for y in xrange(0, M):
			field_x[y]= []
		field[x] = field_x

	particles = []

	for index in xrange(0, len(in_particles)):
		x = in_particles[index]["x"]
		y = in_particles[index]["y"]
		vx = in_particles[index]["vx"]
		vy = in_particles[index]["vy"]
		#TODO ADD TO FIELD
		field[int(floor(x * M / L))][int(floor(y * M / L))].append({"part": index, "x": x, "y": y, "vx": vx, "vy": vy, "x_c": int(floor(x * M / L)), "y_c": int(floor(y * M / L))})

	return field

def generate(N, L):
	particles = []
	for part in xrange(1, N + 1):
		x = random.random() * (L)
		y = random.random() * (L)
		angle = random.random() * 2 * pi
		vx = cos(angle) * 0.03
		vy = sin(angle) * 0.03
		color = get_color(angle)
		particles.append({ "x": x, "y": y, "vx": vx, "vy": vy, "color":color})
	return particles

def get_info(particles, i):
	string = ""
	string += '\t' + str(len(particles)) + '\n'
	string += '\t' + str(i) + '\n'
	for particle in particles:
		string += '\t' + str(particle["x"]) + '\t' + str(particle["y"]) + '\t' + str(particle["vx"]) + '\t' + str(particle["vy"]) + '\t' + str(0.25) + '\t' + str(particle["color"]["R"]) + '\t' + str(particle["color"]["G"]) + '\t' + str(particle["color"]["B"]) + '\n'
	return string

def save_file(file_string):
	with open('output/aneighbours.txt', 'w') as outfile:
		outfile.write(file_string)

def start(M , L, particles, rc, eta):
	i = 0

	file_string = ""
	while i < 1000:
		print i
		field = get_field(M = M, L = L, in_particles = copy.deepcopy(particles))

		neighbours = map(lambda (index, particle): (index, get_neighbours(field = field, particle = particle, rc = rc, M = M, L = L)), enumerate(particles))
		# HERE "part" no available, get enum ^


		file_string += get_info(particles,i)

		x_sum = 0
		y_sum = 0

		for (index,particle) in enumerate(particles):
			particle["x"]= (particle["x"] + particle["vx"] ) % L # dt = 1
			particle["y"]= (particle["y"] + particle["vy"] ) % L
			x_sum += particle["x"]
			y_sum += particle["y"]
			particle_neighbours = neighbours[index][1]
			sum_speed = reduce(lambda speed, neighbour: (speed[0] + neighbour["vy"]/0.03, speed[1] + neighbour["vx"]/0.03), particle_neighbours, (0,0))
			angle = (numpy.random.uniform(-eta/2,eta/2) +
					atan2(sum_speed[0]/len(particle_neighbours),sum_speed[1]/len(particle_neighbours)) )
			particle["vx"]= cos(angle)
			particle["vy"]= sin(angle)
			particle["color"]= get_color(angle)

		va = sqrt(x_sum**2 + y_sum**2) / (len(particles) *0.03)
		i+=1


	file_string += get_info(particles,i)
	save_file(file_string)


def main():

	arguments = parse_arguments()
	
	init()

	with open(arguments['config']) as data_file:
		global data
		data = json.load(data_file)

	pprint.pprint(data)

	M = data['world']["M"] if 'world' in data else data["M"] 
	L = data['world']["L"] if 'world' in data else data["L"]
	rc = data['world']["rc"] if 'world' in data else data["rc"]
	N = data['world']["N"] if 'world' in data else data["N"]
	eta = data['world']["eta"] if 'world' in data else data["eta"]
	particles = data['particles'] if 'particles' in data else generate(N = N, L = L)

	density = N/(L**2)

	start(M = M, L = L, rc = rc, particles = particles, eta = eta)	


if __name__ == '__main__':
	main()