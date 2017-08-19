import json
import ipdb
import pprint
import colored_traceback
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import getopt
import random
import time

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

def get_neightbours(field, particle, rc, M, L, border_control):
	possible_neightbours = []
	x_c = particle["x_c"]
	y_c = particle["y_c"]
	x = particle["x"]
	y = particle["y"]
	xm1 = (x_c - 1) % M
	xp1 = (x_c + 1) % M
	ym1 = (y_c - 1) % M
	yp1 = (y_c + 1) % M
	x2py2 = x ** 2 + y ** 2
	possible_neightbours.extend(field[xm1][ym1]) if border_control or (xm1 >= 0 and ym1 >= 0)  else noop()
	possible_neightbours.extend(field[xm1][y_c]) if border_control or xm1 >= 0  else noop()
	possible_neightbours.extend(field[xm1][yp1]) if border_control or (xm1 >= 0 and yp1 < M)  else noop()
	possible_neightbours.extend(field[x_c][ym1]) if border_control or ym1 >= 0  else noop()
	possible_neightbours.extend(field[x_c][y_c]) 
	possible_neightbours.extend(field[x_c][yp1]) if border_control or ym1 < M  else noop()
	possible_neightbours.extend(field[xp1][ym1]) if border_control or (xp1 < M and ym1 >= 0) else noop()
	possible_neightbours.extend(field[xp1][y_c]) if border_control or xp1 < M  else noop()
	possible_neightbours.extend(field[xp1][yp1]) if border_control or (xp1 < M and yp1 < M) else noop()
	
	#TODO Border control
	#ipdb.set_trace()
	if border_control:
		neightbours = filter(lambda part: ( 
			(L - abs(part["x"]-x))**2+(L-abs(part["y"]-y))**2 < (rc + part["r"]+ particle["r"])**2
			or 
			(part["x"]-x)**2+(L-abs(part["y"]-y))**2 < (rc + part["r"]+ particle["r"])**2
			or 
			(L - abs(part["x"]-x))**2+(part["y"]-y)**2 < (rc + part["r"]+ particle["r"])**2
			or
			(part["x"]-x)**2+(part["y"]-y)**2 < (rc + part["r"]+ particle["r"])**2
			)
			and particle["part"] != part["part"], possible_neightbours)
	else:
		neightbours = filter(lambda part: (part["x"]-x)**2+(part["y"]-y)**2 < (rc + part["r"]+ particle["r"])**2
			and particle["part"] != part["part"], possible_neightbours)
	
	neightbours = map(lambda particle: particle["part"], neightbours)
	return neightbours

def analyse_system(M, L, rc, N, in_particles = [], border_control= False):
	
	print('analizing system')

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
		particles.append({"part": index, "x": x, "y": y, "x_c": x / M, "y_c": y / M, "r": in_particles[index]["r"]})
		field[x / M][y / M].append({"part": index, "x": x, "y": y, "x_c": x / M, "y_c": y / M, "r": in_particles[index]["r"]})

	neightbours = map(lambda particle: (particle["part"], get_neightbours(field, particle, rc = rc, M = M, L = L, border_control = border_control)), particles)
	return neightbours

def brute_force(L, rc, N, in_particles = [], border_control= False):
	
	neightbours = []
	
	for i in xrange(0,len(in_particles)):
		xi = in_particles[i]["x"]
		yi = in_particles[i]["y"]
		
		i_neightbours = []

		for j in xrange(0,len(in_particles)):
			xj = in_particles[j]["x"]
			yj = in_particles[j]["y"]
		
			dif_x__2 = (L-abs(xi-xj))**2 if border_control and (xi-xj)**2 > (L/2)**2 else (xi-xj)**2 
			dif_y__2 = (L-abs(yi-yj))**2 if border_control and (yi-yj)**2 > (L/2)**2 else (yi-yj)**2 
			
			#ipdb.set_trace()

			if dif_x__2 + dif_y__2 < (rc + in_particles[i]["r"] + in_particles[j]["r"])**2 and i != j:
				i_neightbours.append(j)

		neightbours.append((i, i_neightbours))

	return neightbours

def main():

	#TODO border in brute force and cell
	#TODO parameter border_control and selected
	#TODO to line 88 and 173
	
	arguments = parse_arguments()

	border_control = arguments['border_control'] if 'border_control' in arguments else False
	selected = arguments['selected'] if 'selected' in arguments else 1

	init()

	with open(arguments['config']) as data_file:
		global data
		data = json.load(data_file)

	pprint.pprint(data)

	M = data["M"]
	L = data["L"]
	rc = data["rc"]
	N = data["N"]
	#TODO ACTIVATE particles = data["particles"]
	particles = []
	r=0

	for part in xrange(1, N + 1):
		x = random.randint(0, L - 1)
		y = random.randint(0, L - 1)
		particles.append({ "x": x, "y": y, "r": 0 })


	start_time = time.time()

	neighbours = analyse_system(M = M, L = L, rc = rc, N = N, border_control = border_control, in_particles = particles)

	print neighbours

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

	start_time = time.time()

	a = brute_force(L = L, rc = rc, N = N, border_control = border_control, in_particles=particles)

	print a

	run_time = time.time() - start_time

	print 'Brute Force Run Time: ', run_time


if __name__ == '__main__':
	main()