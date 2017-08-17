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

colored_traceback.add_hook()

def init():
	folders = ['images','output']
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

def get_neightbour(field, particule, r ,rc, M, border_control):
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
	
	neightbours = filter(lambda part: (part["x"]-x)**2+(part["y"]-y)**2 < (rc + r)**2
		and particule["part"] != part["part"], possible_neightbours)
	return neightbours

def analyse_system(M, L, rc, N):
	#reduce(lambda accum, i: acumm.add(i,reduce(lambda accum_2, j: accum_2.add(j,{}),xrange(1,M),{})),xrange(1,M),{})

	given = 1

	field = {} 
	for x in xrange(0, M):
		field_x = {} 
		for y in xrange(0, M):
			field_x[y]= []
		field[x] = field_x

	particules = []

	for part in xrange(1, N):
		x = random.randint(0, L-1)
		y = random.randint(0, L-1)
		particules.append({"part":part, "x":x, "y":y, "x_c":x/M, "y_c":y/M})
		field[x/M][y/M].append({"part":part, "x":x, "y":y, "x_c":x/M, "y_c":y/M})

	#TODO ****************************************************r of part or generic **** border control by parameter
	neightbours = map(lambda particule: get_neightbour(field,particule,r=0,rc=rc, M=M, border_control=True), particules)

	import ipdb
	ipdb.set_trace()

	a = 5


def main():

	#TODO time millis
	#TODO complete generation
	#TODO brute force

	arguments = parse_arguments()

	init()

	with open(arguments['config']) as data_file:
		global data
		data = json.load(data_file)

	pprint.pprint(data)

	M = data["M"] or 6
	L = data["L"] or 2
	rc = data["rc"] or 1
	r = data["r"] or 0
	N = data["N"] or 10

	analyse_system(M = M, L = L, rc = rc, N = N)

if __name__ == '__main__':
	main()