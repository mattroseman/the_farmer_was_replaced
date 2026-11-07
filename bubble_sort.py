import drone
import cactus_farm

WORLD_SIZE = get_world_size()

ascending_sort = True

# checks is west neighbor should be swapped, and swaps them
# returns True if swap made
def swap_west_neighbor(west_size=None, current_size=None):
	if west_size == None:
		west_size = measure(West)
	if current_size == None:
		current_size = measure()
		
	if west_size == None or current_size == None:
		return False
	
	if ascending_sort:
		if west_size > current_size:
			swap(West)
			return True
	else:
		if west_size < current_size:
			swap(West)
			return True
	
	return False
		
# checks is south neighbor should be swapped, and swaps them
# returns True if swap made
def swap_south_neighbor(south_size=None, current_size=None):
	if south_size == None:
		south_size = measure(South)
	if current_size == None:
		current_size = measure()

	if south_size == None or current_size == None:
		return False
	
	if ascending_sort:
		if south_size > current_size:
			swap(South)
			return True
	else:
		if south_size < current_size:
			swap(South)
			return True
	
	return False

# checks if neighbors should be swapped, and swaps them
# returns True if any swaps were made
def swap_neighbors():
	swaps_made = False
	last_swap_made = False

	measure_survey = drone.look_around(measure, True)
	if measure_survey[West] == None or measure_survey[South] == None:
		if measure_survey[West] == None and measure_survey[South] != None:
			last_swap_made = swap_south_neighbor(measure_survey[South], measure_survey['current'])
		elif measure_survey[South] == None and measure_survey[West] != None:
			last_swap_made = swap_west_neighbor(measure_survey[West], measure_survey['current'])
		
		return last_swap_made

	if measure_survey[West] > measure_survey[South]:
		last_swap_made = swap_south_neighbor(measure_survey[South], measure_survey['current'])
		swaps_made = swaps_made or last_swap_made
		
		# if previous swap made, use wapped measurement in arguments
		if last_swap_made:
			last_swap_made = swap_west_neighbor(measure_survey[West], measure_survey[South])
		else:
			last_swap_made = swap_west_neighbor(measure_survey[West], measure_survey['current'])
		swaps_made = swaps_made or last_swap_made
	else:
		last_swap_made = swap_west_neighbor(measure_survey[West], measure_survey['current'])
		swaps_made = swaps_made or last_swap_made
		
		# if previous swap made, use swapped measurement in arguments
		if last_swap_made:
			last_swap_made = swap_south_neighbor(measure_survey[South], measure_survey[West])
		else:
			last_swap_made = swap_south_neighbor(measure_survey[South], measure_survey['current'])
		swaps_made = swaps_made or last_swap_made
			
	return swaps_made

# runs a pass through the world, visiting each neighbor and swapping if they're out of order
def bubble_sort_pass():
	sorted = False
	
	while not sorted:
		swap_state = [False]
		
		def track_swaps(swaps_made):
			if swaps_made:
				swap_state[0] = True
		
		drone.for_each_plot(swap_neighbors, track_swaps)
		
		# if no swaps were made, consider world sorted
		sorted = not swap_state[0]

	return sorted

# sort's the world by measurement(), ascending order in x and y direction
def sort(ascending=True):
	ascending_sort = ascending
	
	drone.move_to(0, 0)
	
	sorted = False
	while not sorted:
		sorted = bubble_sort_pass()

	return
	
if __name__ == '__main__':
	# clear()
	# cactus_farm.plant_world()
	sort()
	
	