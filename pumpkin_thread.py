import utils
import crops
import drone
import drone_thread
import partitioner
import routines

WORLD_SIZE = get_world_size()
# min width and height for pumpkin to be harvested
PUMPKIN_SIZE = 6
PATCH_SIZE = PUMPKIN_SIZE + 1
MAX_WORLD_USED = (WORLD_SIZE // PATCH_SIZE) * PATCH_SIZE - 1

def patch_coords_to_world(patch_zero=(0, 0), patch_coords=(0, 0)):
	return (patch_zero[0] + patch_coords[0], patch_zero[1] + patch_coords[1])

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

def farm_patch_rows(args):
	(patch_zero, rows, should_stop) = args

	num_rows = len(rows)
	if num_rows < 1:
		utils.error('drone not given any rows to farm')

	# each zig or zag calls this callback with the row's measurements
	def collect_row_measurements(measurements):
		if len(set(measurements)) == 1:
			harvest()

	while should_stop == None or not should_stop():
		routines.zig_zag_area(
			patch_zero,
			(patch_zero[0] + PUMPKIN_SIZE - 1, patch_zero[1] + num_rows - 1),
			plant_and_measure,
			None,
			collect_row_measurements
		)	
	
		# for row in rows:
		# 	local = (0, row)
		# 	(world_x, world_y) = patch_coords_to_world(patch_zero, local)
		# 	drone.move_to(world_x, world_y)

		# 	measurements = []

		# 	measurement = plant_and_measure()
		# 	measurements.append(measurement)

		# 	for _ in range(PUMPKIN_SIZE - 1):
		# 		move(East)
		# 		local = utils.shift(local, East)

		# 		measurement = plant_and_measure()
		# 		measurements.append(measurement)

		# 	# if each plot of this row has one measurement, the pumpkin's full size
		# 	if len(set(measurements)) == 1: 
		# 		harvest()
		

def farm(should_stop: function=None):
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

	# # divide up the rows of each patch for the drones that will work it
	# rows = []  # row[0] is the list of rows for the first drone, row[0][0] is the first row for the first drone
	# all_rows = list(range(0, PUMPKIN_SIZE))
	# row_starts = list(range(0, PUMPKIN_SIZE, PUMPKIN_SIZE// drones_per_patch))
	# for i in range(drones_per_patch - 1):
	# 	row_start = row_starts[i]
	# 	rows.append(all_rows[row_start:row_starts[i + 1]])
	# # make the last drone get whatever's left, including remainder
	# rows.append(all_rows[row_starts[-1]:])

	for patch_i in range(num_patches):
		first_patch = patch_i == 0
		patch_zero = patch_coordinates[patch_i]

		for drone_i in range(drones_per_patch):
			first_drone = drone_i == 0

			if not (first_drone and first_patch):
				go_to_patch_and_farm = drone_thread.build_move_to_and_doer(
					patch_zero,
					farm_patch_rows,
					(patch_zero, drone_rows[drone_i], should_stop)  # args for farm_patch_rows
				)
				drone_thread.new_thread(go_to_patch_and_farm)

	# the first set of rows for the first patch hwas withheld, so now do that
	# now that child drones are spawned, go do that
	farm_patch_rows(((0, 0), drone_rows[0], should_stop))


if __name__ == '__main__':
	clear()
	farm()