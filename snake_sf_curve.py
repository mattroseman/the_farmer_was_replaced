import drone
import utils
import routines

WORLD_SIZE = get_world_size()

(x, y) = (0, 0)
apple = None
tail_len = 2
tail_path = [(0, 0)]
drone_direction = North
in_excursion = False
floor = 1
ceiling = WORLD_SIZE - 1

# checks if you are within the bounds to safely make an excursion to the apple
def in_excursion_bounds(position, direction_facing):
	global tail_len
	
	# only make excursions within these bounds
	if position[1] < floor or position[1] > ceiling:
		return False
	if direction_facing == East or direction_facing == West:
		return False
	
	if direction_facing == North:
		# if you're on the ceiling
		if position[1] == ceiling:
			return True

		return_y = position[1] + 1
		distance_to_turnaround = ceiling - return_y - 1
	else:
		# if you're on the floor
		if position[1] == floor:
			return True

		return_y = position[1] - 1
		distance_to_turnaround = return_y - 1
		
	if distance_to_turnaround < tail_len // 2:
		return False
	# position[1] > tail_len // (position[0] + 1)
			
	return True
	

# take the drone on an excursion to the apple and back, if there's a straight path
# if no straight path, the do nothing
def excursion(position):
	apple_direction = utils.direction(position, apple)
	apple_dist = utils.distance_no_wrap(position, apple)
	starting_drone_direction = drone_direction
	
	if not in_excursion_bounds(position, starting_drone_direction):
		return
	
	if apple_direction == East:
		for _ in range(apple_dist):
			smove(East)
			
		if position == ceiling:
			smove(South)
		elif position == floor:
			smove(North)
		elif starting_drone_direction == North:
			smove(North)
		else:
			smove(South)
			
		for _ in range(apple_dist):
			smove(West)
			
# add a floor, when tail is so long it'll remain for the rest of the zig-zag run
def make_floor():
	global x
	global y
	global tail_len
	global floor

	if tail_len < WORLD_SIZE:
		return False
	
	if y <= floor + 1:
		if y == floor + 1:
			smove(South)
		
		for _ in range(WORLD_SIZE - x - 1):
			smove(East)
		smove(North)
		for _ in range(WORLD_SIZE - x - 2):
			smove(West)
			
		floor += 1
		
		return True
		
	return False

# add a ceiling, when tail is so long it'll remain for the rest of the zig-zag run
def make_ceiling():
	global x
	global y
	global ceiling
	
	if tail_len < WORLD_SIZE:
		return False
	
	if y >= ceiling  - 1:
		if y == ceiling - 1:
			smove(North)
		
		for _ in range(WORLD_SIZE - x - 1):
			smove(East)
		smove(South)
		for _ in range(WORLD_SIZE - x - 2):
			smove(West)
			
		ceiling -= 1
			
		return True
		
	return False
	
def smove(direction):
	global x
	global y
	global apple
	global tail_len
	global tail_path
	global drone_direction
	global in_excursion
	
	move(direction)
	(x, y) = (get_pos_x(), get_pos_y())
	tail_path.insert(0, (x, y))
	tail_path = tail_path[:tail_len]
	drone_direction = direction
	
	if (x, y) == apple:
		apple = measure()
		
		tail_len += 1
		
	if x == apple[0] or y == apple[1]:
		if not in_excursion:
			in_excursion = True
			excursion((x, y))
			in_excursion = False
			
	x = get_pos_x()
	y = get_pos_y()
		
	return (x, y)

def zig_zag():
	global x
	global y
	global apple
	global ceiling
	global floor
	
	drone.move_to(0, 0)
	
	smove(North)

	for zig_zag_i in range(WORLD_SIZE // 2):
		made_floor_or_ceiling = False


		while y < ceiling:
			if ceiling - y < 2 and y == apple[1] and make_ceiling():
				made_floor_or_ceiling = True
			else:
				smove(North)
		smove(East)
		
		# TODO do a sidewayz zig_zag down the end to fill the space
		# last_ziz_zag = i == (WORLD_SIZE // 2) - 1l
		# if last_zig_zag and WORLD_SIZE % 2 != 0:
			# pass
		
		while y > floor:
			if y - floor < 2 and y == apple[1] and make_floor():
				made_floor_or_ceiling = True
			else:
				smove(South)
		
		# if the apple is to the left, break out of the zig zag and start from the beginning
		if apple[0] < x and tail_len < (x - 1) * WORLD_SIZE:
			break
		
		if not made_floor_or_ceiling:
			smove(East)
	
	# end of the zig zag, now go back to (0, 0) along the bottom row
	smove(South)
	for i in range(WORLD_SIZE - 1, 0, -1):
		smove(West)

def farm():
	global apple

	apple = measure()

	while True:
		routines.zig_zag_farm()

if __name__ == '__main__':
	clear()
	change_hat(Hats.Dinosaur_Hat)
	farm()