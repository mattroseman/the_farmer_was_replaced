# comparator(a, b) returns true if a is greater than b
# sorts ascending order
# available_drones: number of new drones this function can spawn
def sort(l, comparator, available_drones=None):
	if available_drones == None:
		available_drones = max_drones() - num_drones() - 1

	# lists of length 1 or 0, just return back
	length = len(l)
	if length <= 1:
		return l
	# for lists of length 2, sort them
	if length == 2:
		if comparator(l[0], l[1]):
			tmp = l[0]
			l[0] = l[1]
			l[1] = tmp
		return l

	# split list into low, high, and pivot
	pivot = l[random()*length//1]
	low_list = []
	high_list = []
	pivot_list = []
	for elem in l:
		if comparator(pivot, elem):
			low_list.append(elem)
		elif comparator(elem, pivot):
			high_list.append(elem)
		else:
			pivot_list.append(elem)

	low_list_child = None
	high_list_child = None
	low_list_drones = available_drones // 2
	high_list_drones = available_drones - low_list_drones

	# thread to handle lowlist
	if low_list_drones > 0:
		low_list_drones -= 1
		low_list_child = spawn_drone(sort, low_list, comparator, low_list_drones)
	else:
		# do it yourself
		low_list = sort(low_list, comparator, available_drones)

	if high_list_drones > 0:
		high_list_drones -= 1
		high_list_child = spawn_drone(sort, high_list, comparator, high_list_drones)
	else:
		# do it yourself
		high_list = sort(high_list, comparator, available_drones)

	# retreive child's finished work (or it'll be set already if you did it yourself)
	if low_list_child != None:
		low_list = wait_for(low_list_child)
	if high_list_child != None:
		high_list = wait_for(high_list_child)

	return low_list + pivot_list + high_list