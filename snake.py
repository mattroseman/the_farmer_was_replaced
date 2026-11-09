import utils
import drone

WORLD_SIZE = get_world_size()

apple = None
loop = []
loop_steps = {}
x = get_pos_x()
y = get_pos_y()
direction_facing = North
tail = [(0,0)]
tail_len = 1

# returns the sequence of positions that loop through every plot in the world
def build_hamilton_loop():
	loop = [(0,0), (0,1)]
	position = (0,1)

	for zig_zag_i in range(WORLD_SIZE // 2):
		last_zig_zag = zig_zag_i == (WORLD_SIZE // 2) - 1

		for _ in range(WORLD_SIZE - 2):
			# move North
			position = (position[0], position[1] + 1)
			loop.append(position)

		# move East
		position = (position[0] + 1, position[1])
		loop.append(position)

		for _ in range(WORLD_SIZE - 2):
			# move South
			position = (position[0], position[1] - 1)
			loop.append(position)

		if not last_zig_zag:
			# move East
			position = (position[0] + 1, position[1])
			loop.append(position)

	# move South
	position = (position[0], position[1] - 1)
	loop.append(position)

	for _ in range(WORLD_SIZE - 2):
		# move West
		position = (position[0] - 1, position[1])
		loop.append(position)

	return loop

# given a loop as a list of positions, convert it to a dictionary of each step of the loop
# where the key is a position in the loop, and the value is the next step
def convert_to_loop_steps(loop):
	loop_steps = {}

	for i in range(len(loop)):
		position = loop[i]
		next_position = loop[(i + 1) % len(loop)]

		step = utils.direction(position, next_position)

		loop_steps[position] = step

	return loop_steps

# returns the distance to the next turnaround, assuming drone is in a zig-zag path
# if drone is outside of zig-zag portion of the loop's path, return None
def distance_to_turnaround():
	# if top half of world
	if y >= WORLD_SIZE // 2:
		return (WORLD_SIZE - 1) - y
	# bottom half of world
	else:
		return y - 1

# calculates if the tail from going on an excursion from this point, will block the
# upcoming loop path
def will_excursion_tail_block_path():
	# if excursion is to the West
	if apple[0] < x:
		return False

	if direction_facing == North:
		distance_to_turnaround = (WORLD_SIZE - 1) - y
	elif direction_facing == South:
		distance_to_turnaround = y - 1

	if tail_len > (distance_to_turnaround * 2):
		return True
		
	return False


# checks if the tail is in the way of the path the excursion will take
def will_tail_block_excursion_path():
	apple_direction = utils.direction((x, y), apple)

	if direction_facing == West:
		return True

	if apple_direction == West:
		if direction_facing == North:
			# check for tail West and North one
			return (x - 1, y + 1) in tail
		if direction_facing == South:
			# check for tail West and South one
			return (x - 1, y - 1) in tail

	return False
	# TODO should simulate excursion, along with tail trail, and confirm excursion path won't cross over tail
	# TODO the simulation should also produce a path which the drone can follow, in other words keep the movement logic DRY
	
def can_make_excursion():
	apple_direction = utils.direction((x, y), apple)

	if (x, y) == apple:
		return False

	# can't go backwards, since tail is behind you
	if apple_direction == utils.OPPOSITE_DIRECTION[direction_facing]:
		return False

	# only make excursions East/West
	if x == apple[0] or y != apple[1]:
		return False

	if direction_facing == North:
		if y > WORLD_SIZE - 3:
			return False
		if y < 2:
			return False
	if direction_facing == South:
		if y > WORLD_SIZE - 1:
			return False
		if y < 4:
			return False
	if direction_facing == East:
		return True
	if direction_facing == West:
		return False

	if will_excursion_tail_block_path():
		return False
	if will_tail_block_excursion_path():
		return False

	return True

# attempts to beeline for apple, and back into loop, if there's space
def excursion():
	if not can_make_excursion():
		return False

	start_direction_facing = direction_facing
	apple_direction = utils.direction((x, y), apple)
	apple_distance = utils.distance_no_wrap((x, y), apple)


	for _ in range(apple_distance):
		smove(apple_direction)

	if start_direction_facing == North:
		smove(North)
	elif start_direction_facing == South:
		smove(South)
	elif start_direction_facing == East:
		if y < WORLD_SIZE // 2:
			smove(North)
		else:
			smove(South)

	for _ in range(apple_distance):
		smove(utils.OPPOSITE_DIRECTION[apple_direction])

	return True

# finds where you are on the loop, and moves one step along its path
def step_along_loop():
	step = loop_steps[(x, y)]

	smove(step)

def smove(direction):
	global x
	global y
	global direction_facing
	global apple
	global tail_len
	global tail
	
	# if we're moving off the apple
	if (x, y) == apple:
		# measure for new apple
		apple = measure()

		# grow the tail
		tail_len += 1

	success = move(direction)
	if not success:
		utils.error("Can't Move")
		return False

	(x, y) = utils.shift((x, y), direction)
	direction_facing = direction


	tail.append((x, y))
	tail = tail[max(0, len(tail)-tail_len):]

	return True

def snake():
	global apple

	if (x, y) not in loop_steps:
		utils.error('Drone position, (' + str(x) + ', ' + str(y) + ') is outside of loop')

	apple = measure()

	can_move = True
	while can_move:
		old_x = x
		old_y = y
		# x & y are globals and change in this function
		step_along_loop()
		if old_x == x and old_y == y:
			can_move = False

		# if lined up with the apple, attempt an excursion
		if (x, y) != apple and (x == apple[0] or y == apple[1]):
			# TODO prevent excursions off of excursions
			excursion()


def farm(should_stop=None):
	global apple
	global loop
	loop = build_hamilton_loop()
	global loop_steps
	loop_steps = convert_to_loop_steps(loop)

	while should_stop == None or not should_stop(): 
		drone.move_to(0, 0)
		change_hat(Hats.Dinosaur_Hat)
		apple = (x, y)

		start_time = get_time()
		start_inventory = utils.get_inventory()

		snake()

		change_hat(Hats.Straw_Hat)

		end_time = get_time()
		runtime = end_time - start_time
		end_inventory = utils.get_inventory()

		utils.print_lines([
			'Game Over',
			'You played for ' + str(runtime // 60) + ' minutes',
			'You farmed ' + str(end_inventory[Items.Bone] - start_inventory[Items.Bone]) + ' bones'
		])

if __name__ == '__main__':
	clear()
	(x, y) = (0, 0)
	farm()