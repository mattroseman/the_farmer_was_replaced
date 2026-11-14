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

benchmark = utils.get_benchmarker()

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

	petals = plant_sunflower()
	results.add((position, petals))
	for _ in range(WORLD_SIZE - 1):
		move(North)
		position = utils.shift(position, North)

		petals = plant_sunflower()
		results.add((position, petals))

	return results

def plant_sunflower():
	if get_ground_type() != Grounds.Soil:
		till()

	plant(Entities.Sunflower)
	return measure()

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

	while not can_harvest():
		pass

	harvest()

def farm(should_stop=None):
	# planting sunflowers took: 5.43 seconds, 33017 ticks
	quick_print('planting sunflowers')
	benchmark()
	positions_and_petals = plant_field()
	(seconds, ticks) = benchmark()
	drone.move_to(0, 0)
	print('planting sunflowers:', seconds, 'seconds,', ticks, 'ticks')
	do_a_flip()

	# aggregating planting data took: 0.23 seconds, 1370 ticks
	quick_print('aggregating petal counts')
	benchmark()
	petal_positions = aggregate_by_petals(positions_and_petals)
	(seconds, ticks) = benchmark()
	print('aggregating planting data:', seconds, 'seconds,', ticks, 'ticks')

	quick_print('harvesting sunflowers')
	benchmark()
	for petal_count in range(15, 6, -1):
		if petal_count not in petal_positions:
			continue

		sunflower_positions = petal_positions[petal_count]
		harvest_sunflowers(sunflower_positions)
	(seconds, ticks) = benchmark()
	print('harvesting sunflowers:', seconds, 'seconds,', ticks, 'ticks')

if __name__ == '__main__':
	clear()
	farm()