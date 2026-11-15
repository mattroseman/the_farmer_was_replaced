# w/out fast dual-spawner planting and w/ water
# planting sunflowers
# plant sunflowers: 6.93 seconds, 42082 ticks
# aggregating petal counts
# aggregate planting data: 0.7 seconds, 4259 ticks
# harvesting sunflowers
# inefficient @ (22,31) ,  11
# inefficient @ (28,29) ,  7
# inefficient @ (31,31) ,  2
# inefficient @ (28,31) ,  5
# harvest sunflowers: 25.01 seconds, 151921 ticks
# total time: 32.8 seconds
# total rate: 231.19 power/s

# w/ fast dual-spawner planting and w/ water
# planting sunflowers
# plant sunflowers: 4.85 seconds, 29458 ticks
# aggregating petal counts
# aggregate planting data: 0.7 seconds, 4259 ticks
# harvesting sunflowers
# harvest sunflowers: 27.21 seconds, 165329 ticks
# total time: 33.46 seconds
# total rate: 227.53 power/s 

# w/ partitioned world and w/ water
# planting sunflowers
# plant sunflowers: 4.75 seconds, 28858 ticks
# aggregating petal counts
# aggregate planting data: 1.71 seconds, 10385 ticks
# harvesting sunflowers
# harvest sunflowers: 21.29 seconds, 129361 ticks
# total time: 28.45 seconds
# total rate: 271.63 power/s

import utils
import drone
import partitioner

WORLD_SIZE = get_world_size()

WATER_CROP = True
WAIT_FOR_FULLY_GROWN = True 

partitions = []
# mapping of position to the index of the corresponding partition in partitions
position_to_partition = {}

# =================== PARTITIONING FARM ===================

def initialize_farm_partitions():
	global partitions
	global position_to_partition

	# already been built
	if len(partitions) > 0 and len(position_to_partition) > 0:
		return

	# one main drone remains and spawns all children
	# or number of plots, if that's smaller
	num_partitions = min(max_drones() - 1, WORLD_SIZE*WORLD_SIZE)

	# sort partitions by distance from origin, ascending from farthest to closest
	def is_closer_to_origin(a, b):
		a_center = (a['zero'][0] + a['width'] // 2, a['zero'][1] + a['height'] // 2)
		b_center = (b['zero'][0] + b['width'] // 2, b['zero'][1] + b['height'] // 2)
		a_dist = utils.distance(a_center, (0, 0))
		b_dist = utils.distance(b_center, (0, 0))

		# a is closer to origin
		return a_dist < b_dist
	partitions = partitioner.partition_region(
		(0, 0),  		  # region origin
		WORLD_SIZE,       # region width
		WORLD_SIZE,       # region height
		num_partitions,
		is_closer_to_origin
	)

	position_to_partition = {}
	for partition_i in range(num_partitions):
		partition = partitions[partition_i]
		for x in range(partition['zero'][0], partition['zero'][0] + partition['width']):
			for y in range(partition['zero'][1], partition['zero'][1] + partition['height']):
				position_to_partition[(x, y)] = partition_i

# =================== PLANTING SUNFLOWERS ===================

def plant_field():
	position = (get_pos_x(), get_pos_y())
	children = set()
	results = set()

	east_stop = WORLD_SIZE // 2
	# west stop is always one right of east stop
	west_stop = (east_stop + 1) % WORLD_SIZE

	west_spawner_child = spawn_drone(spawn_column_drones, West, position, west_stop)

	move(East)
	position = utils.shift(position, East)
	parent_results = spawn_column_drones(East, position, east_stop)
	for result in parent_results:
		results.add(result)

	west_spawner_results = wait_for(west_spawner_child)
	for result in west_spawner_results:
		results.add(result)

	return results

# moves along the current row, spawning a column drone for each column visited
# drone ends on stop_x, and then works that column itself
def spawn_column_drones(direction, position, stop_x):
	children = set()
	results = set()

	while position[0] != stop_x:
		child = spawn_drone(plant_column, position)
		children.add(child)

		move(direction)
		position = utils.shift(position, direction)

	# ends on stop column
	parent_results = plant_column(position)
	for result in parent_results:
		results.add(result)


	for child in children:
		child_results = wait_for(child)
		for result in child_results:
			results.add(result)

	return results

def plant_column(position):
	results = set()

	petals = plant_sunflower(position)
	results.add((position, petals))
	for _ in range(WORLD_SIZE - 1):
		move(North)
		position = utils.shift(position, North)

		petals = plant_sunflower(position)
		results.add((position, petals))

	return results

def plant_sunflower(position):
	if get_ground_type() != Grounds.Soil:
		till()

	if should_water(position) and get_water() < 0.5:
		use_item(Items.Water)

	plant(Entities.Sunflower)
	return measure()

def should_water(position):
	# return position[1] > 27 or position[0] > 30
	# return utils.distance(position, (0, 0)) > 10
	return WATER_CROP

# =================== ROLLING-UP PETAL COUNTS ===================

# rollup the set of positions for each unique petal count
# positions_and_petals: is an iterable of tuples (position, num_petals)
def aggregate_by_petals(positions_and_petals):
	# petals -> partition -> position
	petal_partitions = {}

	for value in positions_and_petals:
		(position, petals) = value
		partition = position_to_partition[position]

		if petals in petal_partitions:
			if partition in petal_partitions[petals]:
				petal_partitions[petals][partition].append(position)
			else:
				petal_partitions[petals][partition] =  [ position ]
		else:
			petal_partitions[petals] = {partition: [ position ]}

	return petal_partitions

# =================== HARVESTING SUNFLOWERS ===================

def harvest_sunflowers(sunflower_partitions):
	children = set()

	# loop through partitions in partitions order, since that's farthest away to closest
	for partition_i in range(len(partitions)):
		if partition_i not in sunflower_partitions:
			continue

		child = spawn_drone(harvest_partition, sunflower_partitions[partition_i])
		children.add(child)

	for child in children:
		wait_for(child)

def harvest_partition(sunflower_positions):
	for position in sunflower_positions:
		drone.move_to(position[0], position[1])
		harvest_sunflower()

def harvest_sunflower():
	if get_entity_type() != Entities.Sunflower:
		return

	if WAIT_FOR_FULLY_GROWN:
		if not can_harvest():
			(x, y) = (get_pos_x(), get_pos_y())
			quick_print('inefficient @', (x, y), ', ', utils.distance((x, y), (0, 0)))
		while not can_harvest():
			pass

	harvest()

def farm(should_stop=None):
	checkpoint = utils.set_checkpoint()

	initialize_farm_partitions()

	# PLANTING
	quick_print('planting sunflowers')
	checkpoint()

	positions_and_petals = plant_field()

	(seconds, ticks, _) = checkpoint()['since_last_check']
	drone.move_to(0, 0)
	quick_print('plant sunflowers:', seconds, 'seconds,', ticks, 'ticks')
	# do_a_flip()

	quick_print('aggregating petal counts')
	checkpoint()

	petal_partitions = aggregate_by_petals(positions_and_petals)

	(seconds, ticks, _) = checkpoint()['since_last_check']
	quick_print('aggregate planting data:', seconds, 'seconds,', ticks, 'ticks')

	# HARVESTING 
	quick_print('harvesting sunflowers')
	checkpoint()

	for petal_count in range(15, 6, -1):
		if petal_count not in petal_partitions:
			continue

		harvest_sunflowers(petal_partitions[petal_count])

	(seconds, ticks, _) = checkpoint()['since_last_check']
	quick_print('harvest sunflowers:', seconds, 'seconds,', ticks, 'ticks')

	(seconds, _, item_diff) = checkpoint()['since_checkpoint']
	quick_print('total time:', seconds, 'seconds')
	rate = item_diff[Items.Power] / seconds
	quick_print('total rate:', rate, 'power/s')

if __name__ == '__main__':
	clear()
	quick_print('---')
	while True:
		farm()