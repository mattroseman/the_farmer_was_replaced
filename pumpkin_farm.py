import drone
import utils
import crops

WORLD_SIZE = get_world_size()
# min width and height for pumpkin to be harvested
PUMPKIN_HARVEST_SIZE = 6
PATCH_SIZE = PUMPKIN_HARVEST_SIZE + 1
MAX_WORLD_USED = (WORLD_SIZE // PATCH_SIZE) * PATCH_SIZE - 1

farm_measurements = utils.get_farm_state_matrix()
pumpkin_sizes = {}

# determines if the given plot should be a pumpkin, given the target pumpkin size
def is_pumpkin_plot(x, y):
	if x > MAX_WORLD_USED or y > MAX_WORLD_USED:
		return False
	if (x + 1) % PATCH_SIZE == 0 or (y+1) % PATCH_SIZE == 0:
		return False
	return True

# checks if the pumpkin at position (x,y) can be harvested
# meaning it's at least the minimum size for harvest
def can_harvest_pumpkin(x, y):
	global farm_measurements

	if get_entity_type() != Entities.Pumpkin or not can_harvest():
		return False

	pumpkin_id = farm_measurements[y][x]
	if pumpkin_id in pumpkin_sizes and pumpkin_sizes[pumpkin_id] >= PUMPKIN_HARVEST_SIZE:
		return True

	# pumpkin_measurement = farm_measurements[y][x]
	# if pumpkin_measurement == None:
	# 	utils.error("No Pumpkin to check for size at (", x, ",", y, ")")

	# # for each possible pumpkin row, check for horizontal streaks of measurements matching current pumpkin
	# for check_y in range(max(y - PUMPKIN_HARVEST_SIZE + 1, 0), min(y + PUMPKIN_HARVEST_SIZE, MAX_WORLD_USED)):
	# 	streak = 0
	# 	for check_x in range(max(x - PUMPKIN_HARVEST_SIZE + 1, 0), min(x + PUMPKIN_HARVEST_SIZE, MAX_WORLD_USED)):
	# 		measurement = farm_measurements[check_y][check_x]
	# 		if measurement == pumpkin_measurement:
	# 			streak += 1
	# 		else:
	# 			streak = 0
	# 			continue

	# 		if streak >= PUMPKIN_HARVEST_SIZE:
	# 			return True

	# # for each possible pumpkin column, check for vertical streaks of measurements matching current pumpkin
	# for check_x in range(max(x - PUMPKIN_HARVEST_SIZE + 1, 0), min(x + PUMPKIN_HARVEST_SIZE, MAX_WORLD_USED)):
	# 	streak = 0
	# 	for check_y in range(max(y - PUMPKIN_HARVEST_SIZE + 1, 0), min(y + PUMPKIN_HARVEST_SIZE, MAX_WORLD_USED)):
	# 		measurement = farm_measurements[check_y][check_x]
	# 		if measurement == pumpkin_measurement:
	# 			streak += 1
	# 		else:
	# 			streak = 0
	# 			continue

	# 		if streak >= PUMPKIN_HARVEST_SIZE:
	# 			return True

	# return False

def replant_adjacent_dead_pumpkin(direction):
	move(direction)
	crops.handle_pumpkin()
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

# updates the known sizes of pumpkins around the given position
def update_pumpkin_sizes(x, y):
	global farm_measurements

	pumpkin_id = farm_measurements[y][x]
	if pumpkin_id == None:
		utils.error("No Pumpkin to check for size at (" + str(x) + ", " + str(y) + ")")

	vertical_pumpkin_size = 1
	# check North
	for check_y in range(y+1, min(y + PUMPKIN_HARVEST_SIZE, MAX_WORLD_USED)):
		if farm_measurements[check_y][x] == pumpkin_id:
			vertical_pumpkin_size += 1
		else:
			break
	# check South
	for check_y in range(y-1, max(y - PUMPKIN_HARVEST_SIZE, -1), -1):
		if farm_measurements[check_y][x] == pumpkin_id:
			vertical_pumpkin_size += 1
		else:
			break

	horizontal_pumpkin_size = 1
	# check East
	for check_x in range(x+1, min(x + PUMPKIN_HARVEST_SIZE, MAX_WORLD_USED)):
		if farm_measurements[y][check_x] == pumpkin_id:
			horizontal_pumpkin_size += 1
		else:
			break
	# check West
	for check_x in range(x-1, max(x - PUMPKIN_HARVEST_SIZE, -1), -1):
		if farm_measurements[y][check_x] == pumpkin_id:
			horizontal_pumpkin_size += 1
		else:
			break

	pumpkin_sizes[pumpkin_id] = max(horizontal_pumpkin_size, vertical_pumpkin_size)


def measure_surroundings(x=None, y=None):
	global farm_measurements

	if x == None:
		x = get_pos_x()
	if y == None:
		y = get_pos_y()
	
	measure_survey = drone.look_around(measure)
	farm_measurements[y][x] = measure_survey['current']
	farm_measurements[(y+1) % WORLD_SIZE][x] = measure_survey[North]
	farm_measurements[y][(x+1) % WORLD_SIZE] = measure_survey[East]
	farm_measurements[(y-1) % WORLD_SIZE][x] = measure_survey[South]
	farm_measurements[y][(x-1) % WORLD_SIZE] = measure_survey[West]

	# if you're on a pumpkin, measure its size
	if get_entity_type() == Entities.Pumpkin and farm_measurements[y][x] != None:
		update_pumpkin_sizes(x, y)

# compares pumpkin IDs in farm_measurements to the tracked pumpkin sizes, and removes any IDs no longer found in farm
def clear_pumpkin_sizes():
	global farm_measurements

	# get distinct pumpkin IDs in farm_measurements
	pumpkin_ids = set()
	for row in farm_measurements:
		for measurement in row:
			if measurement != None:
				pumpkin_ids.add(measurement)

	pumpkins_to_remove = []
	for pumpkin_id in pumpkin_sizes:
		if pumpkin_id not in pumpkin_ids:
			pumpkins_to_remove.append(pumpkin_id)
	for pumpkin_id in pumpkins_to_remove:
		pumpkin_sizes.pop(pumpkin_id)
	
# 199,065.6 Pumpkin / minute
def farm(should_stop=None):
	while should_stop == None or not should_stop():
		# traverse all rows
		for y in range(MAX_WORLD_USED + 1):
			for x in range(WORLD_SIZE):
				measure_surroundings(x, y)
				if is_pumpkin_plot(x, y):
					if can_harvest_pumpkin(x, y):
						pumpkin_id = measure()
						harvest()
						pumpkin_sizes.pop(pumpkin_id)
						
					# don't waste time handling if there's a good pumpkin already here
					if get_entity_type() != Entities.Pumpkin or not can_harvest():
						crops.handle_pumpkin()
				else:
					pass
					# crops.handle_carrot()
					
				replant_adjacent_dead_pumpkins()
				
				move(East)
			move(North)

		drone.move_to(0, 0)

		# after doing a pass of the farm, clear out any no-longer-found pumpkins
		clear_pumpkin_sizes()
				
if __name__ == '__main__':		
	clear()
	utils.performance_test_farm(farm, 5*60)