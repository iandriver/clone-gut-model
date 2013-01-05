import numpy as np
import matplotlib.pyplot as plt
import random
import itertools
import collections


clone_dict = {"c_isc":0, "c_eb":0, "c_ec":0, "c_ee":0}
non_clone_dict = {"isc":0, "eb":0, "ec":0, "ee":0}

total =20
size_row = 10
size_col = 10
fraction_isc = .05
fraction_ee = .1
fraction_ec = .85
ec_mean_death= 7
ee_mean_death = 10
isc_mean_death = 20
isc_mean_divide = 2
isc_prob_sym_divide =0.02
upd_level =[100, 80, 60] #[ec, ee, isc]


#create 2D area of cells with dimensions sizeXsize
#seed each position with a cell identity at the ratio specified
#and add that cell to the non_clone_dict
#no isc's can be created on edges
area= [ [ 0 for i in range(size_row) ] for j in range(size_col) ]
for d1 in range(size_row):
	for d2 in range(size_col):
		prob = random.random()
	    	if prob <= fraction_ec:
	        	area[d1][d2]= 'ec'
	        	non_clone_dict["ec"]+=1
	        elif prob>fraction_ec and prob<=(fraction_ec+fraction_ee):
	        	area[d1][d2]= 'ee'
	        	non_clone_dict["ee"]+=1
	        elif d1 != 0 or d1 != size_row-1 or d2 !=0 or d2!= size_col-1:
	        	area[d1][d2]= 'isc'	
	        	non_clone_dict["isc"]+=1
#seed a map that will keep track of the age of each cell start all at zero for now 
age_area = [ [ 0 for i in range(size_row) ] for j in range(size_col) ]

#seed a map that will keep track of the level of upd at each cell position zero to start 
upd_area = [ [ 0 for i in range(size_row) ] for j in range(size_col) ]
#seed a map that will keep track of the level of dpp at each cell position zero to start 
dpp_area = [ [ 0 for i in range(size_row) ] for j in range(size_col) ]
       	
# find any cell will return an list of [x y] positions for the cell_type searched
def find_any_cell(area, cell_type):
	pos = []
	count = 0
	for index, item in enumerate(area):
		for val, c in enumerate(item):
			if c == cell_type:
				pos += [index, val]
				count+=1
		pos_array = zip(*[iter(pos)]*2)
	return [pos_array, count]

#create clone by removing one isc from non_clone_dict
#and adding it to clone_dict	
[isc_pos, isc_count] = find_any_cell(area, "isc")
choice = random.randint(0,isc_count-1)
area[isc_pos[choice][0]][isc_pos[choice][1]] = "c_isc"
non_clone_dict["isc"]-=1
clone_dict["c_isc"]+=1



def is_isc(area, x, y):
	if area[x][y] == 'isc' or area[x][y] == 'c_isc':
		return True
	else:
		return False

def flatten(l):
    for el in l:
        if isinstance(el, collections.Iterable) and not isinstance(el, basestring):
            for sub in flatten(el):
                yield sub
        else:
            yield el

# isc_list will return tuples of positions of all iscs
def isc_list(area):
	[isc_pos, isc_count] = find_any_cell(area, "isc")
	[c_isc_pos, isc_count] = find_any_cell(area, "c_isc")
	isc_pos.append(c_isc_pos)
	all_pos = flatten(isc_pos)
	array_pos = zip(*[iter(all_pos)]*2)
	array_pos.sort()	
	return array_pos	

#seed a map isc_div_list that keeps track of the last time an isc divided in form [x,y,days since div]		
isc_div_list = isc_list(area)
for cell in range(len(isc_div_list)):
	isc_div_list[cell] = isc_div_list[cell] + (0,)


#to be called whenever cells move, will take new (x,y) and update isc_div_list if affected
#for updating the div_list when a cell is removed
#check if removed cell is in same row, if in column before isc then update with new column
#returns new isc_div_list 
def new_div_list(x,y,isc_div_list, add_or_remove):
		for place, cells in enumerate(isc_div_list):
			if add_or_remove == "remove" and cells[0] == x:
				if cells[1] > y:
					new_y = cells[1] -1
					isc_div_list.remove((cells[0], cells[1],cells[2]))
					isc_div_list.append((cells[0], new_y,cells[2]))
					isc_div_list.sort()
			elif add_or_remove == "add" and cells[0] == x:
				if cells[1] > y:
					new_y = cells[1] +1
					isc_div_list.remove((cells[0], cells[1],cells[2]))
					isc_div_list.append((cells[0], new_y,cells[2]))
					isc_div_list.sort()							
		return isc_div_list	

#remove cell from map, dict and age map
def remove_cell(x,y, age_area, isc_div_list, area):
	new_row = area[x]
	new_row_age = age_area[x]
	cell_lost = new_row[y]
	del new_row[y]
	del new_row_age[y]
	del area[x]
	del age_area[x]
	area.insert(x,new_row)
	age_area.insert(x,new_row_age)
	if cell_lost == 'isc' or cell_lost =='ec' or cell_lost =='ee':
		non_clone_dict[cell_lost]-=1
		if cell_lost == 'isc':
			for index, value in enumerate(isc_div_list):
				if value[0]==x and value[1] ==y:
					del isc_div_list[index]
		else:
			new_isc_div_list = new_div_list(x, y, isc_div_list, "remove")				
	else:
		clone_dict[cell_lost]-=1	
		if cell_lost == 'c_isc':
			for index, value in enumerate(isc_div_list):
				if value[0]==x and value[1] ==y:
					del isc_div_list[index]
		else:
			new_isc_div_list = new_div_list(x, y, isc_div_list, "remove")	
	isc_div_list = new_isc_div_list

			
#add cell of cell_type at position (x,y)
#set the age of that cell to zero
def add_cell(x,y, area, age_area, cell_type, isc_div_list):
	new_row = area[x]
	new_row_age = age_area[x]	
	new_row.insert(y,cell_type)
	new_row_age.insert(y, 0)
	del area[x]
	del age_area[x]	
	area.insert(x,new_row)
	age_area.insert(x,new_row_age)
	new_isc_div_list = new_div_list(x, y, isc_div_list, "add")		
	if cell_type == 'c_eb' or cell_type == 'c_isc':
		clone_dict[cell_type]+=1
	else:
		non_clone_dict[cell_type]+=1	
	isc_div_list = new_isc_div_list
	

#neigbor will return True if the cell is a neighbor of (x,y) Eight cells are neighbors
def neighbor(x,y,n_x,n_y):
	#acceptable neighbor values
	x_true_list = [x,x+1,x-1]
	y_true_list = [y,y+1,y-1]
	#exclude the starting position
	if n_x != x or n_y != y:
		return n_x in x_true_list and n_y in y_true_list
	else:
		return False

# returns not actual distance but a value corresponding to how many shells (8-cell rings) away the target position is
def distance_value(x,y,t_x, t_y):
	dist = abs(x-t_x)+abs(y-t_y)
	if dist == 1 or dist == 0:
		return 1
	else:	
		for i in range(1,dist+1):
			if neighbor(x,y,t_x, t_y):
				return 1
			elif i == dist and (x == t_x or y == t_y):
				return i-1
			elif i == dist and (x != t_x and y != t_y):
				return i-2


#upd_diffuse function will take a value from a position and add some portion of that value to all squares 
#will be run each death and be additive, rate of diffusion to be determined 


#create an array of same diminsions with all zeros return array and number of elements
def create_blank(area):
	count = 0
	blank_area = area
	for x in range(len(area)):
		for y in range(len(area[x])):
			blank_area[x][y] = 0
			count+=1
	return [blank_area, count]		

#will iterate over area_done marking of searched points and assigning upd levels from point of origin (o_x, o_y)
#initialize with x = o_x and y = o_y will assign 1/distance^2 value, distance being 8-cell shells 
def diffuse_from_point(x, y, upd_area, upd_level, cell_type):	
	if cell_type == 'ec' or cell_type == 'c_ec':
		upd = upd_level[0]
	elif cell_type == 'ee' or cell_type == 'c_ee':
		upd = upd_level[1]
	elif cell_type == 'isc' or cell_type == 'c_isc':
		upd = upd_level[2] 
	new_upd_area = upd_area
	new_upd_area[x][y] = upd
	for x_axis, val in enumerate(upd_area):
		#print x_axis, val
		for y_axis, v in enumerate(val):
			#print "("+str(x_axis)+", "+str(y_axis)+")"
			if x_axis != x or y_axis != y:
				#print "value "+ str(upd/distance_value(x_axis, y_axis, x, y)**2)
				new_upd_area[x_axis][y_axis] += upd/distance_value(x_axis, y_axis, x, y)**2
				#print new_upd_area
	return new_upd_area      



#death function
#removes cell if the age is greater than a number randomly generated from the normal distribution
#each cell type has it's own mean age of death
def cell_death(x,y, age_area, upd_area, dpp_area, upd_level, area, isc_div_list):		
	new_row = area[x]
	cell_type = new_row[y]
	if cell_type == 'ec' or 'c_ec':
		if random.normalvariate(ec_mean_death,1) < age_area[x][y]:
			remove_cell(x,y,area, isc_div_list, area)
			new_upd_area = diffuse_from_point(x, y, upd_area, upd_level, cell_type)
		else:
			new_upd_area = upd_area
	elif cell_type == 'ee' or 'c_ee':
		if random.normalvariate(ee_mean_death,1) < age_area[x][y]:
			remove_cell(x,y,area, isc_div_list, area)
			diffuse_from_point(x, y, upd_area, upd_level, cell_type)
		else:
			new_upd_area = upd_area	
	elif cell_type == 'isc' or 'c_isc':
		if random.normalvariate(isc_mean_death,1) < age_area[x][y]:
			remove_cell(x,y,area, isc_div_list, area)
			diffuse_from_point(x, y, upd_area, upd_level, cell_type)
		else:
			new_upd_area = upd_area
	else:
		new_upd_area = upd_area
	return new_upd_area

#will return a random neighbor of input (x,y)
#the top edge wraps around cells at the side cannot divide out
def choose_direction(x,y):
	check = 0
	while check == 0:
		rand_direction = random.randint(1,5)
		if rand_direction == 1 and x!= 0:
			return [(x-1),y]
			check+=1
		elif rand_direction == 2 and y != (size-1):
			return [x,(y+1)]
			check+=1
		elif rand_direction == 3 and x != (size-1):
			return [(x+1),y]
			check+=1
		elif rand_direction == 4 and y != 0:
			return [x,(y-1)]
			check+=1
		elif rand_direction == 1 and x == 0:
			return [9,y]
			check+=1
		elif rand_direction == 3 and x != (size-1):
			return [0,y]
			check+=1

# divide function will check isc at (x,y) if the randomly generated value of normal distribution is 
#than time last divided add a new cell 'eb' or 'c_eb' depending on type of isc
def isc_divide(x,y, isc_div_list, area, upd_area, upd_level,isc_prob_sym_divide):
	rand_sym_div = random.random()
	print rand_sym_div
	age_to_divide = random.normalvariate(isc_mean_divide,0.5)
	print "age to divide ("+str(x)+", "+str(y)+") = "+str(age_to_divide)
	if area[x][y] != 'isc' and area[x][y] != 'c_isc':
		print "this is not an isc"
	else:
		for pos, i in enumerate(isc_div_list):
			if i[0] == x and i[1] == y:
				since_last_div = i[2]
				isc_num = pos
		direction = choose_direction(x,y)
		if area[x][y] == 'isc' and upd_area[x][y] >= random.normalvariate(upd_level[0]/4,8):
			print "dividing"
			if age_to_divide < since_last_div and rand_sym_div >= isc_prob_sym_divide:
				add_cell(direction[0],direction[1],area, age_area, "eb")
				isc_div_list[isc_num][2] = 0	
			elif age_to_divide < since_last_div and rand_sym_div <= isc_prob_sym_divide:
				add_cell(direction[0],direction[1],area, age_area, "isc")
				isc_div_list[isc_num][2] = 0
		elif area[x][y] == 'c_isc' and upd_area[x][y] >= random.normalvariate(upd_level[0],8):	
			print "dividing"	
			if age_to_divide < since_last_div and rand_sym_div >= isc_prob_sym_divide:	
				add_cell(direction[0],direction[1], area, age_area, "c_eb")
				isc_div_list[isc_num][2] = 0
			elif age_to_divide < since_last_div and rand_sym_div <= isc_prob_sym_divide:
				add_cell(direction[0],direction[1],area, age_area, "c_isc")
				isc_div_list[isc_num][2] = 0

days =10

for t in range(days):
	for r in area:
		for c in r:
				

#print row and col enumerated version of area
def print_enum(area):	
	for index, item in enumerate(area):
		print index
		for i, t in enumerate(item):
			print i, t
