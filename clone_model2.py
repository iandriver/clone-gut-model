import numpy as np
import matplotlib.pyplot as plt
import random

clone_dict = {"c_isc":0, "c_eb":0, "c_ec":0, "c_ee":0}
non_clone_dict = {"isc":0, "eb":0, "ec":0, "ee":0}

total =20
size = 10
fraction_isc = .05
fraction_ee = .1
fraction_ec = .85
ec_mean_death= 7
ee_mean_death = 10
isc_mean_death = 20
isc_mean_divide = 2
isc_prob_sym_divide =0.02

#create 2D area of cells with dimensions sizeXsize
#seed each position with a cell identity at the ratio specified
#and add that cell to the non_clone_dict
#no isc's can be created on edges
area= [ [ 0 for i in range(size) ] for j in range(size) ]
for d1 in range(size):
	for d2 in range(size):
		prob = random.random()
	    	if prob <= fraction_ec:
	        	area[d1][d2]= 'ec'
	        	non_clone_dict["ec"]+=1
	        elif prob>fraction_ec and prob<=(fraction_ec+fraction_ee):
	        	area[d1][d2]= 'ee'
	        	non_clone_dict["ee"]+=1
	        elif d1 != 0 or d1 != size-1 or d2 !=0 or d2!= size-1:
	        	area[d1][d2]= 'isc'	
	        	non_clone_dict["isc"]+=1
#seed a map that will keep track of the age of each cell start all at zero for now 
age_area = [ [ 0 for i in range(size) ] for j in range(size) ]
       	
# find any cell will return an list of [x y] positions for the cell_type searched
def find_any_cell(area, cell_type):
	pos = []
	for index, item in enumerate(area):
		print index, item
		for val, c in enumerate(item):
			if c == cell_type:
				pos += [index, val]
	pos_array =np.array(pos)
	pos_array = np.reshape(pos_array,((len(pos_array)/2),-1))
	return pos_array
	
#create clone by removing one isc from non_clone_dict
#and adding it to clone_dict	
isc_pos = find_any_cell(area, "isc")
choice = random.randint(0,len(isc_pos)-1)
area[isc_pos[choice,0],isc_pos[choice,1]] = "c_isc"
non_clone_dict["isc"]-=1
clone_dict["c_isc"]+=1

#seed a map isc_div_list that keeps track of the last time an isc divided in form [x,y,days since div]
isc_list = []
for x in range(0,len(isc_pos)):
	for i in range(0,3):
		if i < 2:
			isc_list.append(isc_pos[x][i])
		else:
			isc_list.append(0)
isc_div_list = [isc_list[i:i+3] for i in range(0,len(isc_list),3)]			

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
	if cell_lost == 'isc' or 'ec' or 'ee':
		non_clone_dict[str(cell_lost)]-=1
		if cell_lost == 'isc'
			for i in isc_div_list:
				if i[0]==x and i[1] ==y:
					del isc_div_list[i]
	else:
		clone_dict[str(cell_lost)]-=1	
	
#add cell of cell_type at position (x,y)
#set the age of that cell to zero
def add_cell(x,y, area, age_area, cell_type):
	new_row = area[x]
	new_row_age = age_area[x]	
	new_row.insert(y,cell_type)
	new_row_age.insert(y, 0)
	del area[x]
	del age_area[x]	
	area.insert(x,new_row)
	age_area.insert(x,new_row_age)		
	if cell_type == 'c_isc' or 'c_ec' or 'c_ee' or 'c_eb':
		clone_dict[str(cell_lost)]+=1
	else:
		non_clone_dict[str(cell_lost)]+=1	


#death function
#removes cell if the age is greater than a number randomly generated from the normal distribution
#each cell type has it's own mean age of death
def cell_death(x,y, age_area, area):
	new_row = area[x]
	cell_type = new_row[y]
	if cell_type == 'ec' or 'c_ec':
		if random.normalvariate(ec_mean_death,1) < age_area[x][y]:
			remove_cell(x,y,area)
	elif cell_type == 'ee' or 'c_ee':
		if random.normalvariate(ee_mean_death,1) < age_area[x][y]:
			remove_cell(x,y,area)			
	elif cell_type == 'isc' or 'c_isc':
		if random.normalvariate(isc_mean_death,1) < age_area[x][y]:
			remove_cell(x,y,area)

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
def isc_divide(x,y, isc_div_list, area):
	if area[x][y] != 'isc' or 'c_isc':
		return "this is not an isc"
		break
	since_last_div = [x[2] for x in isc_div_list if x[0] == x and x[1] == y]
	direction = choose_direction(x,y)
	if area[x][y] == 'isc':
		if random.normalvariate(isc_mean_divide,2) < since_last_div:
			add_cell(direction[0],direction[1], age_area, "eb")
	elif area[x][y] == 'c_isc':		
		if random.normalvariate(isc_mean_divide,2) < since_last_div:	
			add_cell(direction[0],direction[1], age_area, "c_eb")	
	
							

#print row and col enumerated version of area
def print_enum(area):	
	for index, item in enumerate(area):
		print index
		for i, t in enumerate(item):
			print i, t    	
	

	
for i in area:
	for j in i:
		if 	
for i in range(total):
	for div in range(0, 
	

		

# evenly sampled time at 200ms intervals
t = np.arange(0., 5., 0.2)

# red dashes, blue squares and green triangles
plt.plot(t, t, 'r--', t, t**2, 'bs', t, t**3, 'g^')
plt.show()