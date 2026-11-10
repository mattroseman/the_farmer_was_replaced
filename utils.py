import drone

WORLD_SIZE = get_world_size()

DIRECTIONS = [North, East, South, West]
OPPOSITE_DIRECTION = {
	North: South,
	East: West,
	South: North,
	West: East
}

# given a (x, y) position and a direction, calculates the new (x, y)
# if you moved one step in the given direction
def shift(position, direction):
	if direction == North:
		return (position[0], position[1] + 1)
	elif direction == East:
		return (position[0] + 1, position[1])
	elif direction == South:
		return (position[0], position[1] - 1)
	elif direction == West:
		return (position[0] - 1, position[1])
		
# direction determines the general direction point b is from a, e.g. a -> b is East
# favors North/South over East/West, e.g NW becomes N and SE becomes South
def direction(a, b):
	if a == b:
		return None

	if b[1] > a[1]:
		return North
	if b[1] < a[1]:
		return South
	if b[0] > a[0]:
		return East
	if b[0] < a[0]:
		return West

# Manhattan distance, with wrapped grid
def distance(a, b):
	return min(
		abs(a[0] - b[0]),
		# wraparound world
		WORLD_SIZE - abs(a[0] - b[0])
	) + min(
		abs(a[1] - b[1]),
		# wraparound world
		WORLD_SIZE - abs(a[1] - b[1])
	)

# distance with no wrap
def distance_no_wrap(a, b):
	return abs(a[0] - b[0]) + abs(a[1] - b[1])
	
def inbounds(position):
	return (
		position[0] >= 0 and position[0] < WORLD_SIZE and
		position[1] >= 0 and position[1] < WORLD_SIZE
	)

TILLED_CROPS = [
	Entities.Carrot,
	Entities.Pumpkin
]

def set_hat_off_crop(crop=Entities.Grass):
	if crop == Entities.Grass:
		change_hat(Hats.Green_Hat)
	elif crop == Entities.Bush:
		change_hat(Hats.Brown_Hat)
	elif crop == Entities.Carrot:
		change_hat(Hats.Carrot_Hat)
	elif crop == Entities.Tree:
		change_hat(Hats.Tree_Hat)
		
# checks if the given array contains an element of the given value
def array_contains(array, value):
	for element in array:
		if element == value:
			return True
	return False

def is_tilled_crop(crop):
	return array_contains(TILLED_CROPS, crop)
	
# generates a matrix x wide and y tall, with the given default value
def get_matrix(x, y, default=None):
	matrix = []
	for _ in range(y):
		row = []
		for _ in range(x):
			row.append(default)
		matrix.append(row)
	
	return matrix
			
def get_farm_state_matrix():
	return get_matrix(get_world_size(), get_world_size(), None)
	
def get_inventory():
	return {
		Items.Hay: num_items(Items.Hay),
		Items.Wood: num_items(Items.Wood),
		Items.Carrot: num_items(Items.Carrot),
		Items.Pumpkin: num_items(Items.Pumpkin),
		Items.Water: num_items(Items.Water),
		Items.Fertilizer: num_items(Items.Fertilizer),
		Items.Power: num_items(Items.Power),
		Items.Cactus: num_items(Items.Cactus),
		Items.Bone: num_items(Items.Bone)
	}

# get_timer creates a timer function which starts a timer when called
# The returned timer function returns False while the timer is active, and True when the time limit has been reached
def get_timer(time_limit_seconds):
	state = [None]  # state[0] = start time

	def timer():
		# If this is the first call, start the timer
		if state[0] == None:
			state[0] = get_time()
			return False
			
		start_time = state[0]

		return (get_time() - start_time) >= time_limit_seconds
	
	return timer
	
# performance_test_farm takes a given farm function, and tracks
# how many resources it's able to produce in a set time.
# to be used for optimizations
# WARNING: THIS FUNCTION CONTAINS AN INFINITE LOOP
def performance_test_farm(farm, time_limit_sec=30):
	start_inventory = get_inventory()
	timer = get_timer(time_limit_sec)
	
	farm(timer)
	
	end_inventory = get_inventory()
	
	# calculate how much was produced
	production = {
		'Hay': end_inventory[Items.Hay] - start_inventory[Items.Hay],
		'Wood': end_inventory[Items.Wood] - start_inventory[Items.Wood],
		'Carrot': end_inventory[Items.Carrot] - start_inventory[Items.Carrot],
		'Pumpkin': end_inventory[Items.Pumpkin] - start_inventory[Items.Pumpkin],
		'Water': end_inventory[Items.Water] - start_inventory[Items.Water],
		'Power': end_inventory[Items.Power] - start_inventory[Items.Power],
		'Cactus': end_inventory[Items.Cactus] - start_inventory[Items.Cactus],
		'Bone': end_inventory[Items.Bone] - start_inventory[Items.Bone]
	}

	drone.move_to(0, min(len(production), get_world_size() - 1))
	
	while True:
		for product in production:
			move(South)
			print((production[product] / time_limit_sec) * 60, product, '/ minute')
		for _ in production:
			move(North)

def copy_list(items):
	copy = []
	for item in items:
		copy.append(item)

	return copy

def randomize_list(items):
	for i in range(len(items)-1, 0, -1):
		j = get_random_num(0, i+1)
		# swap i and j
		tmp = items[i]
		items[i] = items[j]
		items[j] = tmp

	return items

def get_randomized_directions():
	directions_copy = copy_list(DIRECTIONS)
	randomize_list(directions_copy)

	return directions_copy

def get_random_direction():
	return DIRECTIONS[random()*4 // 1]

# returns a random number from range_min, inclusive, to range_max, exclusive
# [range_min, range_max)
def get_random_num(range_min, range_max):
	if range_max <= range_min:
		error('range_max must be larger than range_min')

	num = ((random() * (range_max - range_min)) // 1) + range_min

	return num

def get_random_plot():
	x = random() * WORLD_SIZE // 1
	y = random() * WORLD_SIZE // 1
	return (x, y)

def coinflip():
	if random() >= 0.50:
		return True
	return False
	
def wait_ticks(ticks):
	# minus three for:
	# 1. tick for the function call
	# 2. tick for the for loop to start
	# 3. tick for math done to subtrack these listed ticks
	for _ in range(ticks - 3):
		# pass takes one tick
		pass

# calls the operation function with args, if args provided
# otherwise calls it without any arguments at all
def optional_args(operation, args=()):
	if args == () or args == None:
		operation()
	else:
		operation(args)

# wraps the call of the given operation with the given args in a
# wrapper function with no args
def with_args(operation, args=()):
	def wrapper():
		if args != () and args != None:
			operation(args)
		else:
			operation

	return wrapper

# prints the given error message, repeatedly
# WARNING: THIS FUNCTION CONTAINS AN INFINITE LOOP
def error(message):
	while True:
		print(message)
		do_a_flip()

def print_lines(lines, forever=False):
	num_lines = len(lines)

	repeat = True
	while repeat:
		drone.move_to(0, num_lines)
		for line in lines:
			move(South)
			print(line)
			do_a_flip()

		if not forever:
			repeat = False
		
if __name__ == '__main__':
	hat = Hats.Traffic_Cone
	change_hat(hat)
	print(hat)