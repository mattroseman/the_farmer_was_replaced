import utils
import crops
import drone
import drone_thread
import partitioner
import routines
import paths

WORLD_SIZE = get_world_size()
# min width and height for pumpkin to be harvested
PUMPKIN_SIZE = 7
PATCH_SIZE = PUMPKIN_SIZE + 1
MAX_WORLD_USED = (WORLD_SIZE // PATCH_SIZE) * PATCH_SIZE - 1

# globals used for each drone to track Pumpkins in their plot
# last measurement from pumpkin's edge
edges = {
	North: None,
	South: None,
	East: None,
	West: None
}
can_track_north_south = False
can_track_east_west = False
edge_north_y = PUMPKIN_SIZE
edge_south_y = 0
edge_east_x = PUMPKIN_SIZE
edge_west_x = 0

planted = set()
plots_done = set()

def reset_tracking():
	global edges
	global planted
	global plots_done

	edges = {
		North: None,
		South: None,
		East: None,
		West: None
	}
	planted = set()
	plots_done = set()

	return edges

# initializes the global edge-tracking variables for the given area
def initialize_edges(area_zero, width, height) -> None:
	global can_track_north_south
	global edge_north_y
	global edge_south_y
	global can_track_east_west
	global edge_east_x
	global edge_west_x

	can_track_north_south = height + 1 >= PUMPKIN_SIZE
	edge_north_y = area_zero[1] + PUMPKIN_SIZE - 1
	edge_south_y = area_zero[1]

	can_track_east_west = width + 1 >= PUMPKIN_SIZE
	edge_east_x = area_zero[0] + PUMPKIN_SIZE - 1
	edge_west_x = area_zero[0]

	if not can_track_north_south and not can_track_east_west:
		utils.error('drone area too small')

def is_grown_pumpkin():
	return get_entity_type() == Entities.Pumpkin and can_harvest()

def replant_adjacent_dead_pumpkin(direction):
	move(direction)
	crops.handle_pumpkin(True)
	# recursively search the adjacent spots to this spot
	replant_adjacent_dead_pumpkins()
	# move back to where you started
	move(utils.OPPOSITE_DIRECTION[direction])
	
def replant_adjacent_dead_pumpkins():
	entity_survey = drone.look_around(get_entity_type)
	if entity_survey[North] == Entities.Dead_Pumpkin:
		replant_adjacent_dead_pumpkin(North)
	if entity_survey[East] == Entities.Dead_Pumpkin:
		replant_adjacent_dead_pumpkin(East)
	if entity_survey[South] == Entities.Dead_Pumpkin:
		replant_adjacent_dead_pumpkin(South)
	if entity_survey[West] == Entities.Dead_Pumpkin:
		replant_adjacent_dead_pumpkin(West)

def plant_and_measure():
	if get_entity_type() != Entities.Pumpkin:
		crops.handle_pumpkin()
	
	replant_adjacent_dead_pumpkins()
		
	measurement = measure()
	return measurement

# assumes drone is on current_plot, as additional look-ahead measurements are
# taken if next to edge
def add_edge_measurement(current_plot, current_measurement) -> None:
	global edges

	plot = current_plot
	measurement = current_measurement

	if can_track_north_south:
		if plot[1] == edge_north_y:
			edges[North] = measurement
		# if you're right before the edge, look ahead
		if plot[1] == edge_north_y - 1:
			north_measurement = measure(North)
			if north_measurement != None:
				edges[North] = north_measurement

		if plot[1] == edge_south_y:
			edges[South] = measurement
		if plot[1] == edge_south_y + 1:
			south_measurement = measure(South)
			if south_measurement != None:
				edges[South] = south_measurement

	if can_track_east_west:
		if plot[0] == edge_east_x:
			edges[East] = measurement
		if plot[0] == edge_east_x - 1:
			east_measurement = measure(East)
			if east_measurement != None:
				edges[East] = (east_measurement)

		if plot[0] == edge_west_x:
			edges[West] = measurement
		if plot[0] == edge_west_x + 1:
			west_measurement = measure(West)
			if west_measurement != None:
				edges[West] = (west_measurement)


def is_pumpkin_fully_grown(current_plot, current_measurement) -> bool:
	pumpkin_fully_grown = False

	add_edge_measurement(current_plot, current_measurement)

	# check if the opposite edges have the same measurement, meaning pumpkin is wide or tall enough
	if can_track_north_south:
		if edges[North] != None and edges[North] == edges[South]:
			pumpkin_fully_grown = True

	if can_track_east_west:
		if edges[East] != None and edges[East] == edges[West]:
			pumpkin_fully_grown = True

	return pumpkin_fully_grown

# continuously checks for the pumpkin to be fully grown, and then harvests
def wait_for_full_pumpkin(should_stop=None):
	position = (get_pos_x(), get_pos_y())
	if can_track_east_west:
		sentry_start = (edge_west_x, position[1])
		sentry_end = (edge_east_x, position[1])
	elif can_track_north_south:
		sentry_start = (position[0], edge_north_y)
		sentry_end = (position[0], edge_south_y)

	while should_stop == None or not should_stop():
		# check if another drone harvested
		if get_entity_type() == None:
			return

		# go back and forth comparing measurements
		drone.move_to(sentry_start[0], sentry_start[1])
		one_measurement = measure()
		drone.move_to(sentry_end[0], sentry_end[1])
		other_measurement = measure()

		if one_measurement != None and one_measurement == other_measurement:
			harvest()
			return

# loops over given area and farms pumpkins, harvesting if pumpkin reaches full size
# args contents:
#	patch_zero
# 	area_zero
# 	width
# 	height
# 	should_stop (optional)
def farm_area(args):
	global can_track_north_south
	global can_track_east_west
	global edge_north_y
	global edge_south_y
	global edge_east_x
	global edge_west_x
	global plots_done

	if len(args) == 4:
		(patch_zero, area_zero, width, height) = args
		should_stop = None
	else:
		(patch_zero, area_zero, width, height, should_stop) = args

	drone_path = paths.build_space_filling_path(area_zero, width, height)

	initialize_edges(patch_zero, width, height)

	# Traverse Path
	while should_stop == None or not should_stop():
		for plot in drone_path:
			# if you've already done this plot, skip it
			if plot in plots_done:
				continue 

			drone.move_to(plot[0], plot[1])

			# if this plot was planted, but is now empty, a harvest happened so reset
			if get_entity_type() == None and plot in planted:
				reset_tracking()

			measurement = plant_and_measure()
			planted.add(plot)
			if measurement != None and is_pumpkin_fully_grown(plot, measurement):
				harvest()

				reset_tracking()

			if is_grown_pumpkin():
				plots_done.add(plot)

			# if every plot is done
			if len(plots_done) == len(drone_path):
				# reset just plots done
				plots_done = set()


def farm(should_stop=None):
	patches_per_side = WORLD_SIZE // PATCH_SIZE
	num_patches = patches_per_side**2

	# list of the bottom/left coordinates of each patch, i.e. local (0, 0)
	patch_coordinates =  []
	for y in range(0, patches_per_side * PATCH_SIZE, PATCH_SIZE):
		for x in range(0, patches_per_side * PATCH_SIZE, PATCH_SIZE):
			patch_coordinates.append((x, y))

	drones_per_patch = min(max_drones() // num_patches, PUMPKIN_SIZE)
	if drones_per_patch < 1:
		utils.error('not enough drones')

	all_rows = list(range(0, PUMPKIN_SIZE))
	drone_rows = partitioner.partition(all_rows, drones_per_patch)

	for patch_i in range(num_patches):
		first_patch = patch_i == 0
		patch_zero = patch_coordinates[patch_i]

		for drone_i in range(drones_per_patch):
			first_drone = drone_i == 0

			if not (first_drone and first_patch):
				min_row = min(drone_rows[drone_i])
				drone_area_zero = (patch_zero[0], patch_zero[1] + min_row)
				drone_area_width = PUMPKIN_SIZE
				drone_area_height = len(drone_rows[drone_i])

				drone_thread.new_thread(
					farm_area,
					None,  # direction
					# arguments to farm_area
					(patch_zero, drone_area_zero, drone_area_width, drone_area_height, should_stop)
				)

	drone_area_height = len(drone_rows[0])
	farm_area(((0, 0), (0, 0), PUMPKIN_SIZE, drone_area_height, should_stop))


if __name__ == '__main__':
	clear()
	
	start_pumpkins = num_items(Items.Pumpkin)
	def enough_pumpkins():
		return num_items(Items.Pumpkin) - start_pumpkins > 200000000

	start_time = get_time()
	farm(enough_pumpkins)
	end_time = get_time()
	
	(minutes, seconds) = utils.seconds_to_minutes_and_seconds(end_time - start_time)
	drone.move_to(0, 0)
	while True:
		print('Pumpkin Farm took: ' + minutes + ' minutes, ' + seconds + ' seconds')
		do_a_flip()