# planting sunflowers
# planting sunflowers: 5.81 seconds, 35277 ticks
# aggregating petal counts
# aggregating planting data: 0.68 seconds, 4111 ticks
# harvesting sunflowers
# harvesting sunflowers: 26.71 seconds, 162264 ticks

import utils
import drone
import partitioner

WORLD_SIZE = get_world_size()

WATER_CROP = True

# =================== PLANTING SUNFLOWERS ===================

def plant_field():
	position = (get_pos_x(), get_pos_y())
	children = set()
	results = set()

	for _ in range(WORLD_SIZE - 1):
		child = spawn_drone(plant_column, position)
		children.add(child)

		move(East)
		position = utils.shift(position, East)

	parent_results = plant_column(position)
	for parent_result in parent_results:
		results.add(parent_result)

	for child in children:
		child_results = wait_for(child)
		for child_result in child_results:
			results.add(child_result)

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
	petal_positions = {}
	for value in positions_and_petals:
		(position, petals) = value

		if petals in petal_positions:
			petal_positions[petals].append(position)
		else:
			petal_positions[petals] = [ position ]

	return petal_positions

# =================== HARVESTING SUNFLOWERS ===================

def harvest_sunflowers(sunflower_positions):
	children = set()
	num_sunflowers = len(sunflower_positions)

	# partition the given set of sunflowes
	available_drones = max_drones() - 1
	num_partitions = min(num_sunflowers, available_drones)
	partition_slices = get_partition_indecies(sunflower_positions, num_partitions)

	for partition_slice in partition_slices:
		(start_i, end_i) = partition_slice
		child = spawn_drone(harvest_partition, sunflower_positions, start_i, end_i)
		children.add(child)

	for child in children:
		wait_for(child)

# calculates the start/end indecies for partitions of the given sunflower positions
# returns: [(0, 10), (10, 20), ...]
def get_partition_indecies(sunflower_positions, num_partitions):
	num_sunflowers = len(sunflower_positions)

	indecies = []
	for i in range(num_partitions):
		start_index = (i * num_sunflowers) // num_partitions
		end_index = ((i + 1) * num_sunflowers) // num_partitions
		indecies.append((start_index, end_index))

	return indecies

def harvest_partition(sunflower_positions, partition_start, partition_end):
	for i in range(partition_start, partition_end):
		position = sunflower_positions[i]
		drone.move_to(position[0], position[1])
		harvest_sunflower()

def harvest_sunflower():
	if get_entity_type() != Entities.Sunflower:
		return

	if not can_harvest():
		(x, y) = (get_pos_x(), get_pos_y())
		quick_print('inefficient @', (x, y), ', ', utils.distance((x, y), (0, 0)))
	while not can_harvest():
		pass

	harvest()

def farm(should_stop=None):
	checkpoint = utils.set_checkpoint()

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

	petal_positions = aggregate_by_petals(positions_and_petals)

	(seconds, ticks, _) = checkpoint()['since_last_check']
	quick_print('aggregate planting data:', seconds, 'seconds,', ticks, 'ticks')

	# HARVESTING 
	quick_print('harvesting sunflowers')
	checkpoint()

	for petal_count in range(15, 6, -1):
		if petal_count not in petal_positions:
			continue

		sunflower_positions = petal_positions[petal_count]
		harvest_sunflowers(sunflower_positions)


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