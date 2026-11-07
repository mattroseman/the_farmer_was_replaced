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

# Manhattan distance, with wrapped grid
def distance(point_a, point_b):
	return min(
		abs(point_a[0] - point_b[0]),
		# wraparound world
		WORLD_SIZE - abs(point_a[0] - point_b[0])
	) + min(
		abs(point_a[1] - point_b[1]),
		# wraparound world
		WORLD_SIZE - abs(point_a[1] - point_b[1])
	)
	
def inbounds(x, y):
	return (
		x >= 0 and x < WORLD_SIZE and
		y >= 0 and y < WORLD_SIZE
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
		Items.Cactus: num_items(Items.Cactus)
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
		'Cactus': end_inventory[Items.Cactus] - start_inventory[Items.Cactus]
	}

	drone.move_to(0, min(len(production), get_world_size() - 1))
	
	while True:
		for product in production:
			move(South)
			print(product, ':', production[product], 'units,', (production[product] / time_limit_sec) * 60, '/ minute')
		for _ in production:
			move(North)

# prints the given error message, repeatedly
# WARNING: THIS FUNCTION CONTAINS AN INFINITE LOOP
def error(message):
	while True:
		print(message)
		do_a_flip()
		
if __name__ == '__main__':
	hat = Hats.Traffic_Cone
	change_hat(hat)
	print(hat)