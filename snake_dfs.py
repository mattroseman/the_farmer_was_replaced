import drone
import utils
import snake

WORLD_SIZE = get_world_size()

# once the tail is this long, stop searching for paths and follow the zig zag loop instead
LOOP_TAIL_LEN = WORLD_SIZE * 2

position = (0, 0)
tail = []
tail_len = 0
apple = (0, 0)

# the zig zag loop through every plot, as a list of positions
loop = []
# position -> direction of the next step along the loop
loop_steps = {}
# position -> index of that position in the loop
loop_indexes = {}

def find_path(start, end, start_tail, visited=None):
	if start == end:
		return []

	if visited == None:
		visited = []

	# get directions favoring those pointing towards the end
	step_direction_distances = {}
	for direction in utils.DIRECTIONS:
		new_position = utils.shift(start, direction)

		if not utils.inbounds(new_position):
			continue
		if new_position in start_tail:
			continue
		if new_position in visited:
			continue

		distance = utils.distance_no_wrap(new_position, end)
		step_direction_distances[direction] = distance

	directions_by_closeness = utils.get_dict_keys_sorted_by_values(step_direction_distances)

	for direction in directions_by_closeness:
		new_position = utils.shift(start, direction)
		sim_tail = start_tail + [new_position]
		sim_tail = sim_tail[max(0, len(sim_tail) - tail_len):]
		visited.append(new_position)

		path = find_path(new_position, end, sim_tail, visited)
		if path == None:
			continue

		path = [direction] + path
		return path

def go_to_apple(apple: tuple[int, int]):
	path = find_path(position, apple, tail)

	if path == None:
		utils.error('no path')

	for step in path:
		smove(step)

def smove(direction):
	global position
	global tail
	global tail_len

	success = move(direction)
	if not success:
		utils.error('Game Over')

	position = utils.shift(position, direction)
	tail.append(position)
	tail = tail[max(len(tail) - tail_len, 0):]

def play_snake():
	global position
	global tail
	global tail_len
	global apple

	drone.move_to(0, 0)
	position = (0, 0)
	change_hat(Hats.Dinosaur_Hat)
	tail = [(0, 0)]
	tail_len = 1

	apple = measure()
	while True:
		go_to_apple(apple)

		tail_len += 1
		apple = measure()
		if apple == None:
			utils.error('Game Over')



if __name__ == '__main__':
	clear()
	play_snake()