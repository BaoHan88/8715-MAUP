#
# Code for Spatial Partitioning.
# Author: Jayant Gupta
# 04/18/2018
#

import matplotlib.pyplot as plt
import copy
import re
from scipy.spatial import ConvexHull
import numpy as np

# PARAMETERS #
# OVERLAP PERCENTAGE : 0.2
# DIFFERENCE IN POPULATION RATIO : 0.15 

# Point input and visualization phase.
fp = open('input1.txt', 'r')
data = fp.read()
lines = data.split('\n')

nrow = int(lines[0].split(' ')[0])
ncol = int(lines[0].split(' ')[1])
npoints = int(lines[1])
X = []
Y = []

matrix = [[0 for x in range(ncol)] for x in range(nrow)]

point_dict = {}
for i in range(npoints):
	x = int(lines[2 + i].split(' ')[0])
	y = int(lines[2 + i].split(' ')[1])
	matrix[y-1][x-1] = 1
	X.append(x)
	Y.append(y)

for row in matrix:
	print(row)

#plt.scatter(X, Y, marker='s')

def check_neighbor(x, y, x_bound, y_bound):
	space_flag = 0 # initial value, space don't exist.
	point_flag = 0
	if (x > 0 and x <= x_bound and y > 0 and y <= y_bound): # space exists
		space_flag = 1 
		if matrix[y-1][x-1] == 1:  # point exists
			point_flag = 1
	return space_flag, point_flag


def stringify_point(x, y):
	return str(x) + "_" + str(y)

# Neighborhood Analysis Phase.
print("NEIGHBORHOOD RATIO")
point_neighbor_ratio = {}
for i in range(len(X)):
	# calculate number of filled neighbors.
	tn = 0 # total neighbor
	pn = 0 # point neighbor
	for j in range(-1, 2):
		for k in range(-1, 2):
			if j == 0 and k == 0:
				continue
			a,b = check_neighbor(X[i] - j, Y[i] - k, nrow, ncol)
			tn += a
			pn += b
	point_neighbor_ratio[stringify_point(X[i], Y[i])] = float(pn) / tn

print point_neighbor_ratio
walk = {}
for i in range(len(X)):
	walk[stringify_point(X[i], Y[i])] = False
# Neighborhood generation Phase - BFS based approach
generation = {}

for i in range(len(X)):
	Q = [(X[i], Y[i])]
	key = stringify_point(X[i], Y[i])
	generation[key] = []
	while(len(Q) > 0):
		point = Q.pop(0)
		x = point[0]
		y = point[1]
		str_point = stringify_point(x,y)
		if(walk[str_point]):
			continue;
		else:
			walk[str_point] = True
		for j in range(-1, 2):
			for k in range(-1, 2):
				if j == 0 and k == 0:
					continue
				if(x-j > 0 and x-j <= ncol and y-k > 0 and y-k <= nrow):
					if matrix[y-k-1][x-j-1] == 0: # Can be replaced by neighbor ratio.
						generation[key].append((x-j, y-k))
					else: # All the points that come in here will have an entry in walk.
						generation[key].append((x-j, y-k))
						Q.append((x-j, y-k))

# Removing Duplicates.
for key in generation:
	val = generation[key]
	generation[key] = list(set(val))

def print_neighborhood(generation):
#	for line in generation:
#		print line, generation[line]
	print "NEIGHBORHOOD GENERATION"
	for key in generation:
		val = generation[key]
		if (len(val) > 0):
			print("-----------" + key + "----------")
			aux = copy.deepcopy(matrix)
			for item in val:
				if(stringify_point(item[0], item[1]) not in walk):
					aux[item[1] - 1][item[0] - 1] = 6
			for row in aux:
				print(row)
			print("-----------XXX----------")


def plot_neighborhood(generation):
	for line in generation:
		points = np.array(list(generation[line]))
		hull = ConvexHull(points)
		plt.plot(points[:,0], points[:,1], 'o')
		for simplex in hull.simplices:
			plt.plot(points[simplex, 0], points[simplex, 1], 'k-')
		plt.plot(points[hull.vertices,0], points[hull.vertices,1], 'r--', lw=2)
		plt.plot(points[hull.vertices[0],0], points[hull.vertices[0],1], 'o')
#	plt.axes([0.85, 0.1, 0.85, 0.1])
	plt.xlim(0,ncol)
	plt.ylim(0,nrow)
	for i in range(len(X)):
		plt.plot(X[i], Y[i], 'bs')
	plt.show()
		

def destringify_point(str_point):
	x_y = str_point.split('_')
	return (int(x_y[0]), int(x_y[1]))

count = 0;
is_used = {}
#Neighborghood aggregation to create jurisdiction areas.
def create_jurisdiction_areas(_generation):
	global count
	pattern = re.compile("ja[0-9]+")
	aggregation = {}
	keys = _generation.keys()
	for i in range(len(keys)):
		key1 = keys[i]
		val1 = set(_generation[key1])
		if not pattern.search(key1):
			val1.add(destringify_point(key1))
		l_v1 = len(val1)
		if not key1 in is_used:
			is_used[key1] = False
		for j in range(i+1, len(keys)):
			key2 = keys[j]
			if not key1 in is_used:
				is_used[key2] = False
			if key1 == key2:
				continue
			val2 = set(_generation[key2])
			if not pattern.search(key2):
				val2.add(destringify_point(key2))
			l_v2 = len(val2)
			if l_v1 == 1 or l_v2 == 1:
				continue
			inter = val1 & val2
			if( (float(len(inter)) / min(l_v1, l_v2) ) > 0.2): #overlap percentage.
				if abs(point_neighbor_ratio[key1] - point_neighbor_ratio[key2]) < 0.15: # Similar region
					is_used[key1] = True
					is_used[key2] = True
					_key = 'ja' + str(count)
					aggregation[_key] = val1 | val2
					point_neighbor_ratio[_key] = (point_neighbor_ratio[key1] * l_v1 + point_neighbor_ratio[key2] * l_v2) / (l_v1 + l_v2 - len(inter))
					count += 1
		if not is_used[key1] and l_v1 > 1:
			aggregation[key1] = val1
	return aggregation

def prune_duplicates(generation):
	to_delete = []
	keys = generation.keys()
	for i in range(len(keys)):
		for j in range(i+1, len(keys)):
			if set(generation[keys[i]]) == set(generation[keys[j]]):
				to_delete.append(keys[j])
	to_delete = list(set(to_delete))
	for key in to_delete:
		del generation[key]
				
for key in generation:
	is_used[key] = False
old_areas = 0
new_areas = len(generation)
for i in range(6):
#	print(old_areas, new_areas)
	prune_duplicates(generation)
#	print_neighborhood(generation)
	generation = create_jurisdiction_areas(generation) 
	old_areas = new_areas
	new_areas = len(generation)

#print(old_areas, new_areas)
prune_duplicates(generation)
#print_neighborhood(generation)
plot_neighborhood(generation)
