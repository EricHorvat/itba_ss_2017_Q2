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

def noop():
	pass

def get_neighbours(field, particle, rc, M, L, border_control):
	possible_neighbours = []
	x_c = particle["x_c"]
	y_c = particle["y_c"]
	x = particle["x"]
	y = particle["y"]
	xm1 = (x_c - 1) % M
	xp1 = (x_c + 1) % M
	ym1 = (y_c - 1) % M
	yp1 = (y_c + 1) % M
	x2py2 = x ** 2 + y ** 2
	possible_neighbours.extend(field[xm1][ym1]) if border_control or (xm1 >= 0 and ym1 >= 0)  else noop()
	possible_neighbours.extend(field[xm1][y_c]) if border_control or xm1 >= 0  else noop()
	possible_neighbours.extend(field[xm1][yp1]) if border_control or (xm1 >= 0 and yp1 < M)  else noop()
	possible_neighbours.extend(field[x_c][ym1]) if border_control or ym1 >= 0  else noop()
	possible_neighbours.extend(field[x_c][y_c]) 
	possible_neighbours.extend(field[x_c][yp1]) if border_control or ym1 < M  else noop()
	possible_neighbours.extend(field[xp1][ym1]) if border_control or (xp1 < M and ym1 >= 0) else noop()
	possible_neighbours.extend(field[xp1][y_c]) if border_control or xp1 < M  else noop()
	possible_neighbours.extend(field[xp1][yp1]) if border_control or (xp1 < M and yp1 < M) else noop()
	
	if border_control:
		neighbours = filter(lambda part: ( 
			(L - abs(part["x"]-x))**2+(L-abs(part["y"]-y))**2 < (rc)**2
			or 
			(part["x"]-x)**2+(L-abs(part["y"]-y))**2 < (rc)**2
			or 
			(L - abs(part["x"]-x))**2+(part["y"]-y)**2 < (rc)**2
			or
			(part["x"]-x)**2+(part["y"]-y)**2 < (rc)**2
			)
			and particle["part"] != part["part"], possible_neighbours)
	else:
		neighbours = filter(lambda part: (part["x"]-x)**2+(part["y"]-y)**2 < (rc)**2
			and particle["part"] != part["part"], possible_neighbours)
	
	neighbours = map(lambda particle: particle["part"], neighbours)
	return neighbours

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
		particles.append({"part": index, "x": x, "y": y, "x_c": int(floor(x * M / L)), "y_c": int(floor(y * M / L))})
		field[int(floor(x * M / L))][int(floor(y * M / L))].append({"part": index, "x": x, "y": y, "x_c": int(floor(x * M / L)), "y_c": int(floor(y * M / L))})

	return field


###############################################
###############################################

def generate(N, L):
	particles = []
	for part in xrange(1, N + 1):
		x = random.random() * (L)
		y = random.random() * (L)
		angle = random.random() * 2 * pi
		vx = cos(angle) * 0.03
		vy = sin(angle) * 0.03
		particles.append({ "x": x, "y": y, "vx": vx, "vy": vy})
	ipdb.set_trace()
	return particles

#####REM
def save(M,L,rc,N,neighbours,particles, i):

	with open('output/neighbours'+i+'.json', 'w') as outfile:
		json.dump({
			'neighbours': neighbours,
			'particles': particles,
			'world': {
				'M': M,
				'L': L,
				'rc': rc,
				'N': N
			}
		}, outfile)
##### REM

def start(M , L, particles, rc, eta):
	i = 0
	while True:
		field = get_field(M = M, L = L, in_particles = copy.deepcopy(particles))

		neighbours = map(lambda particle: (particle["part"], get_neighbours(field, particle, rc = rc, M = M, L = L, border_control = border_control)), particles)
		# HERE "part" no available, get enum ^


		####REMOVE
		save(M = M, L = L, rc = rc, particles = particles, neighbours = neighbours, eta = eta, i = i)
		i+=1
		#####

		for particle in particles:
			particle["x"]= (particle["x"] + particle["vx"] ) % L # dt = 1
			particle["y"]= (particle["y"] + particle["vy"] ) % L
			particle_neighbours = neighbours[particle["part"]][1]
			particle_neighbours.append(particle)
			sum_vel = reduce(lambda neighbour, vel: (vel[0] + neighbour["vy"]/0.03, vel[1] + neighbour["vx"]/0.03), particle_neighbours, (0,0))
			angle = (numpy.random.uniform(-eta/2,eta/2) +
					atan2(sum_vel[0]/len(possible_neighbours),sum_vel[1]/len(possible_neighbours)) )
			particle["vx"]= cos(angle)
			particle["vy"]= sin(angle)

def main():

	###TODO 
	### Calclate density
	### Calclate order
	arguments = parse_arguments()

	border_control = arguments['border_control'] if 'border_control' in arguments else False
	
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

	start(M = M, L = L, rc = rc, particles = particles, eta = eta)	

	run_time = time.time() - start_time

	with open('output/neighbours.json', 'w') as outfile:
		json.dump({
			'neighbours': neighbours,
			'particles': particles,
			'world': {
				'M': M,
				'L': L,
				'rc': rc,
				'r': r,
				'N': N
			}
		}, outfile)

	print 'Run Time: ', run_time


if __name__ == '__main__':
	main()