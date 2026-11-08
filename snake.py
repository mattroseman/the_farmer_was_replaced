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

def can_make_excursion():
	if (x, y) == apple:
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

	move(direction)
	(x, y) = utils.shift((x, y), direction)
	direction_facing = direction

	if measure() != None:
		apple = measure()
		tail_len += 1
		print(tail)

	tail.append((x, y))
	tail = tail[max(0, len(tail)-tail_len):]

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

		if (x, y) != apple and (x == apple[0] or y == apple[1]):
			excursion()


def farm(should_stop=None):
	global loop
	loop = build_hamilton_loop()
	global loop_steps
	loop_steps = convert_to_loop_steps(loop)

	while should_stop == None or not should_stop(): 
		drone.move_to(0, 0)
		change_hat(Hats.Dinosaur_Hat)

		start_time = get_time()
		start_inventory = utils.get_inventory()

		snake()

		change_hat(Hats.Straw_Hat)

		end_time = get_time()
		runtime = end_time - start_time
		end_inventory = utils.get_inventory()

		utils.print_lines([
			'You Won!',
			'You beat snake in ' + str(runtime // 60) + ' minutes',
			'You farmed ' + str(end_inventory[Items.Bone] - start_inventory[Items.Bone]) + ' bones'
		])

if __name__ == '__main__':
	clear()
	(x, y) = (0, 0)
	farm()