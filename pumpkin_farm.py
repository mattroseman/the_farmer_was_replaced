import drone
import utils
import crops

WORLD_SIZE = get_world_size()
# min width and height for pumpkin to be harvested
PUMPKIN_HARVEST_SIZE = 6
PATCH_SIZE = PUMPKIN_HARVEST_SIZE + 1
MAX_WORLD_USED = (WORLD_SIZE // PATCH_SIZE) * PATCH_SIZE - 1

farm_measurements = utils.get_farm_state_matrix()

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
	if get_entity_type() != Entities.Pumpkin or not can_harvest():
		return False
	
	# check horizontally for the same measurement wide enough for a pumpkin
	previous_measurement = None
	streak = 1
	for i in range(max(x - PUMPKIN_HARVEST_SIZE + 1, 0), min(x + PUMPKIN_HARVEST_SIZE, MAX_WORLD_USED)):
		check_x = i % WORLD_SIZE
		check_y = y
			
		measurement = farm_measurements[check_y][check_x]
		if measurement == None:
			continue
			
		if measurement == previous_measurement:
			streak += 1
		else:
			streak = 1
			previous_measurement = measurement
			
	if streak >= PUMPKIN_HARVEST_SIZE:
		return True
	
	previous_measurement = None
	streak = 1
	
	# check vertically for the same measurement tall enough for a pumpkin
	for j in range(max(y - PUMPKIN_HARVEST_SIZE + 1, 0), min(y + PUMPKIN_HARVEST_SIZE - 1, MAX_WORLD_USED)):
		check_x = x
		check_y = j % WORLD_SIZE
			
		measurement = farm_measurements[check_y][check_x]
		if measurement == None:
			continue
			
		if measurement == previous_measurement:
			streak += 1
		else:
			streak = 1
			previous_measurement = measurement
			
	if streak >= PUMPKIN_HARVEST_SIZE:
		return True
		
	return False

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
		
def measure_surroundings(x=None, y=None):
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
	
# Carrot : -23696 units, -4739.2 / minute
# Pumpkin : 103680 units, 20736 / minute
def farm(should_stop=None):
	while should_stop == None or not should_stop():
		# traverse all rows
		for y in range(MAX_WORLD_USED + 1):
			for x in range(WORLD_SIZE):
				measure_surroundings(x, y)
				if is_pumpkin_plot(x, y):
					if can_harvest_pumpkin(x, y):
						harvest()
						
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
				
if __name__ == '__main__':		
	clear()
	utils.performance_test_farm(farm, 5*60)