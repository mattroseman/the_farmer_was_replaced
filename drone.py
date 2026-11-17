import utils
import crops

WORLD_SIZE = get_world_size()


SPECIAL_HATS = [
	Hats.Dinosaur_Hat,
	Hats.Dynamite_Hat,
	Hats.Mining_Hat
]

unlocked_hats = set()
def get_hats():
	global unlocked_hats

	if len(unlocked_hats) > 0:
		return unlocked_hats

	unlocked_hats = set()

	for hat in Hats:
		if num_unlocked(hat) > 0 and hat not in SPECIAL_HATS:
			unlocked_hats.add(hat)

	return unlocked_hats

def get_random_hat():
	hats = list(get_hats())
	return hats[random() * len(hats) // 1]

def wear_random_hat():
	hat = get_random_hat()
	change_hat(hat)


def move_to_no_warp(x, y):
	target_x = x
	target_y = y
	current_x = get_pos_x()
	current_y = get_pos_y()
	
	if target_x >= WORLD_SIZE:
		utils.error('ERROR: move_to x is outside of world')
	if target_y >= WORLD_SIZE:
		utils.error('ERROR: move_to y is outside of world')
		
	while (current_x, current_y) != (target_x, target_y):
		if target_x != current_x:
			if target_x < current_x:
				move(West)
				current_x -= 1
			else:
				move(East)
				current_x += 1
		if target_y != current_y:
			if target_y < current_y:
				move(South)
				current_y -= 1
			else:
				move(North)
				current_y += 1
	
def move_to(x, y):
	target_x = x
	target_y = y
	current_x = get_pos_x()
	current_y = get_pos_y()
	
	if target_x >= WORLD_SIZE:
		utils.error('ERROR: move_to x is outside of world')
	if target_y >= WORLD_SIZE:
		utils.error('ERROR: move_to y is outside of world')
	
	while (current_x, current_y) != (target_x, target_y):
		if target_x != current_x:
			if (target_x - current_x) % WORLD_SIZE < (current_x - target_x) % WORLD_SIZE:
				move(East)
			else:
				move(West)
			
			current_x = get_pos_x()
		
		if target_y != current_y:
			if (target_y - current_y) % WORLD_SIZE < (current_y - target_y) % WORLD_SIZE:
				move(North)
			else:
				move(South)
				
			current_y = get_pos_y()

def move_to_center():
	center = (WORLD_SIZE // 2, WORLD_SIZE // 2)
	move_to(center[0], center[1])

# 5 ticks overhead + 200 ticks/num_moves
# tick-optimized moves in one direction
def precise_move_n(direction, num_moves):
	# 1 tick
	two_steps = num_moves // 2

	# 2 ticks
	for _ in range(two_steps):
		# 200 ticks
		move(direction)
		# 200 ticks
		move(direction)

	# 2 ticks
	if num_moves % 2:
		# 200 ticks
		move(direction)

# 10 base, 7 / axis moved, 200 / step
# optimized, yet convoluted, version of move_to()
# minimum & predictible number of ticks
def precise_move_to(start: tuple[int, int], end: tuple[int, int]) -> None:
	# 0 tick
	(start_x, start_y) = start
	# 0 tick
	(end_x, end_y) = end

	# 2 tick
	start_y_diff = (start_y - end_y) % WORLD_SIZE
	# 2 tick
	end_y_diff = (end_y - start_y) % WORLD_SIZE
	# 2 tick
	start_x_diff = (start_x - end_x) % WORLD_SIZE
	# 2 tick
	end_x_diff = (end_x - start_x) % WORLD_SIZE

	# TODO try only modular arithmetic when in if statement

	# 1 ticks
	if start_x_diff:
		# 2 ticks
		if end_x_diff < start_x_diff:
			# 5 ticks overhead + 200 ticks/num_moves
			precise_move_n(East, end_x_diff)
		else:
			# 5 ticks overhead + 200 ticks/num_moves
			precise_move_n(West, start_x_diff)

	# 1 ticks
	if start_y_diff:
		# 2 ticks
		if end_y_diff < start_y_diff:
			# 5 ticks overhead + 200 ticks/num_moves
			precise_move_n(North, end_y_diff)
		else:
			# 5 ticks overhead + 200 ticks/num_moves
			precise_move_n(South, start_y_diff)

# calculates the tick cost of a movement from start to end,
# using precise_move_to above
def quote_precise_move_cost(start, end) -> int:
	(start_x, start_y) = start
	(end_x, end_y) = end

	axis_x_changes = start_x != end_x
	axis_y_changes = start_y != end_y

	num_steps = utils.distance(start, end)

	return 10 + 7*axis_x_changes + 7*axis_y_changes + 200*num_steps 

			
def look_around(sense, no_wrap=False):
	# if no_wrap specified, don't look past the world edges, to the other side
	if no_wrap:
		x = get_pos_x()
		y = get_pos_y()
		
		survey = {
			'current': sense(),
			North: None,
			East: None,
			South: None,
			West: None
		}
		if y < WORLD_SIZE - 1:
			survey[North] = sense(North)
		if x < WORLD_SIZE - 1:
			survey[East] = sense(East)
		if y > 0:
			survey[South] = sense(South)
		if x > 0:
			survey[West] = sense(West)
			
		return survey
		
	return {
		'current': sense(),
		North: sense(North),
		East: sense(East),
		South: sense(South),
		West: sense(West)
	}

def is_top_right():
	x = get_pos_x()
	y = get_pos_y()
	world_size = get_world_size()
	
	return x == world_size - 1 and y == world_size - 1
	
def wait_around():
	while True:
		pass

def do_nothing():
	pass

# waits for the given crop in the given direction
# optional timeout after the given number of ticks
# returns True if the observed crop is the waited-for one, False if there was a timeout
def wait_for_crop(crop, direction, timeout_ticks=None):
	observed_crop = None
	start_tick = get_tick_count()
	while observed_crop != crop and (timeout_ticks == None or get_tick_count() - start_tick < timeout_ticks):
		observed_crop = get_entity_type(direction)

	return observed_crop == crop

# waits for any crop except the given set of exceptions
# returns the observed crop
def wait_for_crop_except(except_crops, direction, timeout_ticks=None):
	observed_crop = None
	start_tick = get_tick_count()
	while (observed_crop == None or observed_crop in except_crops) and (timeout_ticks == None or get_tick_count() - start_tick < timeout_ticks):
		observed_crop = get_entity_type(direction)

	if observed_crop != None and observed_crop not in except_crops:
		return observed_crop

	return None

# waits for any change in crop from the given direction
# returns the new crop or False if there was a timeout
# an empty plot doesn't count, so if the starting entity is harvested, this function won't return until a new, different, crop is then planted
def wait_for_new_crop(direction, timeout_ticks=None):
	starting_entity = get_entity_type(direction)
	observed_crop = starting_entity
	start_tick = get_tick_count()
	while (observed_crop == starting_entity or observed_crop == None) and (timeout_ticks == None or get_tick_count() - start_tick < timeout_ticks):
		observed_crop = get_entity_type(direction)

	if observed_crop != starting_entity:
		return observed_crop

	return False


				
if __name__ == '__main__':
	move_to(1,1)
	do_a_flip()
	move_to(4,5)
	do_a_flip()
	move_to(3,3)
			