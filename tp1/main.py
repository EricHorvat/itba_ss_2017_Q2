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
	print('usage: python main.py [options]')
	print('-h --help:	 print this screen')
	print('-c --config=:  configuration file')

def parse_arguments():
	arguments = {
		'config': './config/config.json',
	}
	try:
		opts, args = getopt.getopt(sys.argv[1:], 'hc:tn', ['help', 'config='])
	
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
		else:
			assert False, 'unknown option `' + o + '`' 

	return arguments

def noop():
	pass

def get_neightbours(field, particule, rc, M, L, border_control):
	possible_neightbours = []
	x_c = particule["x_c"]
	y_c = particule["y_c"]
	x = particule["x"]
	y = particule["y"]
	xm1 = (x_c-1)%M
	xp1 = (x_c+1)%M
	ym1 = (y_c-1)%M
	yp1 = (y_c+1)%M
	x2py2=x**2+y**2
	possible_neightbours.extend(field[xm1][ym1]) if border_control or (xm1 >= 0 and ym1 >= 0)  else noop()
	possible_neightbours.extend(field[xm1][y_c]) if border_control or xm1 >= 0  else noop()
	possible_neightbours.extend(field[xm1][yp1]) if border_control or (xm1 >= 0 and yp1 < M)  else noop()
	possible_neightbours.extend(field[x_c][ym1]) if border_control or ym1 >= 0  else noop()
	possible_neightbours.extend(field[x_c][y_c]) 
	possible_neightbours.extend(field[x_c][yp1]) if border_control and ym1 < M  else noop()
	possible_neightbours.extend(field[xp1][ym1]) if border_control and (xp1 < M and ym1 >= 0) else noop()
	possible_neightbours.extend(field[xp1][y_c]) if border_control and xp1 < M  else noop()
	possible_neightbours.extend(field[xp1][yp1]) if border_control and (xp1 < M and yp1 < M) else noop()
	
	#TODO Border control
	if border_control:
		neightbours = filter(lambda part: (
			(L-abs(part["x"]-x))**2+(L-abs(part["y"]-y))**2 < (rc + part["r"]+ particule["r"])**2
			or
			(part["x"]-x)**2+(part["y"]-y)**2 < (rc + part["r"]+ particule["r"])**2
			)
			and particule["part"] != part["part"], possible_neightbours)
	else:
		neightbours = filter(lambda part: (part["x"]-x)**2+(part["y"]-y)**2 < (rc + part["r"]+ particule["r"])**2
			and particule["part"] != part["part"], possible_neightbours)
	
	neightbours = map(lambda particule: particule["part"], neightbours)
	return neightbours

def analyse_system(M, L, rc, N, in_particules = [], border_control= True):
	
	field = {} 
	for x in xrange(0, M):
		field_x = {} 
		for y in xrange(0, M):
			field_x[y]= []
		field[x] = field_x

	particules = []

	for index in xrange(0, len(in_particules)):
		x = in_particules[index]["x"]
		y = in_particules[index]["y"]
		particules.append({"part":index, "x":x, "y":y, "x_c":x/M, "y_c":y/M, "r":in_particules[index]["r"]})
		field[x/M][y/M].append({"part":index, "x":x, "y":y, "x_c":x/M, "y_c":y/M, "r":in_particules[index]["r"]})

	neightbours = map(lambda particule: (particule["part"], get_neightbours(field,particule, rc=rc, M=M, L=L, border_control=border_control)), particules)
	return neightbours

def brute_force(L, rc, N, in_particules = [], border_control= True):
	
	neightbours = []
	
	for i in xrange(0,len(in_particules)):
		xi = in_particules[i]["x"]
		yi = in_particules[i]["y"]
		
		i_neightbours = []

		for j in xrange(0,len(in_particules)):
			xj = in_particules[j]["x"]
			yj = in_particules[j]["y"]
		
			dif_x__2 = (xi-xj)**2 if border_control and (xi-xj)**2 > (L/2)**2 else (L-abs(xi-xj))**2 
			dif_y__2 = (yi-yj)**2 if border_control and (yi-yj)**2 > (L/2)**2 else (L-abs(yi-yj))**2
			dif_x__2 = (xi-xj)**2 
			dif_y__2 = (yi-yj)**2

			if dif_x__2 + dif_y__2 < (rc + in_particules[i]["r"] + in_particules[j]["r"])**2 and i != j:
				i_neightbours.append(j)

		neightbours.append((i,i_neightbours))

	return neightbours

def main():

	#TODO border in brute force and cell
	# Result to console, time OK

	arguments = parse_arguments()

	#TODO arguments get border_control
	border_control = True
	#TODO arguments get selected
	selected = 1

	init()

	with open(arguments['config']) as data_file:
		global data
		data = json.load(data_file)

	pprint.pprint(data)

	M = data["M"]
	L = data["L"]
	rc = data["rc"]
	r = data["r"]
	N = data["N"]
	#TODO ACTIVATE particules = data["particules"]
	particules = []

	for part in xrange(1, N+1):
		x = random.randint(0, L-1)
		y = random.randint(0, L-1)
		particules.append({"x":x,"y":y,"r":0})


	start_time = time.time()

	print analyse_system(M = M, L = L, rc = rc, N = N, border_control = border_control, in_particules = particules)

	run_time = time.time() - start_time

	print run_time

	start_time = time.time()

	a = brute_force(L = L, rc = rc, N = N, border_control = border_control, in_particules=particules)

	run_time = time.time() - start_time

	print run_time

	ipdb.set_trace()



if __name__ == '__main__':
	main()