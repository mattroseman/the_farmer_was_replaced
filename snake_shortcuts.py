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

# checks if moving in the given shortcut direction will lead to you being blocked by your tail, assuming you continue on loop
def will_shortcut_lead_to_tail_block(shortcut):
	sim_tail = tail
	sim_position = (x, y)

	# get the index where the shortcut takes you
	shortcut_start = utils.shift(sim_position, shortcut)
	for i in range(len(loop)):
		if shortcut_start == loop[i]:
			shortcut_start_loop_i = i
			break

	# step through the loop, tail-length times, to see if you'll run into your tail
	loop_segment = loop[shortcut_start_loop_i:(shortcut_start_loop_i + tail_len) % len(loop)]
	for sim_position in loop_segment:
		if sim_position in sim_tail:
			return True

		sim_tail.append(sim_position)
		sim_tail = sim_tail[1:]

	return False

# finds where you are on the loop, and moves one step along its path
def step_along_loop():
	step = loop_steps[(x, y)]
	
	next_position = utils.shift((x, y), step)
	next_apple_dist = utils.distance_no_wrap(next_position, apple)

	# check if a different step, towards the apple, would then trap you by your tail
	for shortcut in utils.DIRECTIONS:
		if shortcut == step:
			continue

		shortcut_position = utils.shift((x, y), shortcut)
		if not utils.inbounds(shortcut_position[0], shortcut_position[1]):
			continue

		shortcut_apple_dist = utils.distance_no_wrap(shortcut_position, apple)
		if shortcut_apple_dist < next_apple_dist and not will_shortcut_lead_to_tail_block(shortcut):
			smove(shortcut)
			return

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
