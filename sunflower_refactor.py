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

# w/ partitioned world and sorted positions and w/ water
# planting sunflowers
# plant sunflowers: 4.75 seconds, 28858 ticks
# aggregating petal counts
# aggregate planting data: 1.71 seconds, 10385 ticks
# harvesting sunflowers
# harvest sunflowers: 21.29 seconds, 129361 ticks
# total time: 28.45 seconds
# total rate: 271.63 power/s

# w/ above & limited range of petal-counts planted
# planting sunflowers
# plant sunflowers: 5.56 seconds, 33790 ticks
# aggregating petal counts
# aggregate planting data: 2.55 seconds, 15473 ticks
# harvesting sunflowers
# harvest sunflowers: 14.1 seconds, 85645 ticks
# total time: 22.9 seconds
# total rate: 337.49 power/s

import utils
import drone
import partitioner

WORLD_SIZE = get_world_size()

WATER_CROP = True
WAIT_FOR_FULLY_GROWN = True
# limit range of measurements during planting
# sunflowers have 7-15 petals
MIN_SUNFLOWER_MEASUREMENT = 10

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
		is_closer_to_origin,
		max_drones() - 1  # make available all drones but this one
	)

	position_to_partition = {}
	for partition_i in range(num_partitions):
		partition = partitions[partition_i]
		for x in range(partition['zero'][0], partition['zero'][0] + partition['width']):
			for y in range(partition['zero'][1], partition['zero'][1] + partition['height']):
				position_to_partition[(x, y)] = partition_i

# =================== PLANTING SUNFLOWERS ===================

def plant_field():
	drone.move_to(0, 0)

	# create drones east and west to spawn further drones to farm east_columns and west_columns
	# don't include column 0 in either east or west, as it'll be handled by self
	east_columns = list(range(1, WORLD_SIZE // 2))
	west_columns = list(range(WORLD_SIZE // 2, WORLD_SIZE))
	east_child = spawn_drone(spawn_drones_to_plant_column_range, East, east_columns)
	west_child = spawn_drone(spawn_drones_to_plant_column_range, West, west_columns)

	# you plant the 0th column yourself
	your_results = plant_column((0, 0))
	# and combine with east and west children
	east_results = wait_for(east_child)
	west_results = wait_for(west_child)

	merge_results(east_results, west_results)
	merge_results(east_results, your_results)
	return east_results 

# spawns drones to plant the plots in the given list of columns, moving in the given direction
# direction: direction drone is moving, to avoid wasted movements
# columns: sorted (west to east) list of columns for this drone to process
def spawn_drones_to_plant_column_range(direction, columns):
	if direction == East:
		drone.move_to(columns[0], 0)
	elif direction == West:
		drone.move_to(columns[-1], 0)
	else:
		utils.error('spawn_drones_to_plant_column_range can only move East or West, not', direction)

	# BASE CASE
	num_columns = len(columns)
	if num_columns == 1:
		results = plant_column((columns[0], 0))
		return results

	available_drones = max_drones() - num_drones()
	if num_columns - 1 > available_drones:
		utils.error('not enough drones')

	# split columns
	first_half_columns = columns[:num_columns // 2]
	second_half_columns = columns[num_columns // 2:]
	if direction == East:
		child_columns = second_half_columns
		your_columns = first_half_columns
	else:
		child_columns = first_half_columns
		your_columns = second_half_columns

	child = spawn_drone(spawn_drones_to_plant_column_range, direction, child_columns)
	if child == None:
		utils.error('failed to spawn drone')

	your_results = spawn_drones_to_plant_column_range(direction, your_columns)
	child_results = wait_for(child)

	# merge your results into child_results
	merge_results(child_results, your_results)
	return child_results

# results returned as a nested dict of measurement petals to partitions
# to positions in that partition which had that number of petals
# {
#   # 15 petals measured
#   "15": {
#		# positions found in position index 3, with 15 petals
#		# sorted by distance from origin (closer first)
#		"3": [(0, 0), (0, 5), ...],
#		"30": [...],
#		...
#	},
#	"14": {...}
# }
def plant_column(position):
	results = {}

	petals = plant_sunflower(position)
	add_measurement_to_results(results, position, petals)

	for _ in range(WORLD_SIZE - 1):
		move(North)
		position = utils.shift(position, North)

		petals = plant_sunflower(position)
		add_measurement_to_results(results, position, petals)

	return results

def add_measurement_to_results(results, position, petals):
	partition = position_to_partition[position]

	if petals in results:
		if partition in results[petals]:
			# keep the list of points w/this number of petals in this partition sorted
			# utils.insert_sorted(results[petals][partition], position, utils.is_farther_from_origin)
			results[petals][partition].append(position)
		else:
			results[petals][partition] = [ position ]
	else:
		# create a new list of positions, with the number of petals, for this partition
		results[petals] = { partition: [ position ] }

	return results

# given two results from plant_column, merge_results combines their measurement data
# keeping lists sorted, and adding keys where necessary
def merge_results(a, b):
	# for data found on this petal count
	for measurement in b:
		if measurement in a:
			# for each partition found with measurement petal count
			for partition in b[measurement]:
				if partition in a[measurement]:
					# merge the sorted positions found in this partition and with this number of petals
					# a[measurement][partition] = utils.merge_sorted_lists(
					# 	a[measurement][partition],
					# 	b[measurement][partition],
					# 	utils.is_farther_from_origin
					# )
					for position in b[measurement][partition]:
						a[measurement][partition].append(position)
				else:
					a[measurement][partition] = b[measurement][partition]
		else:
			a[measurement] = b[measurement]

	return a

def plant_sunflower(position):
	if get_ground_type() != Grounds.Soil:
		till()

	if should_water(position) and get_water() < 0.5:
		use_item(Items.Water)

	plant(Entities.Sunflower)
	measurement = measure()
	while measurement < MIN_SUNFLOWER_MEASUREMENT:
		harvest()
		plant(Entities.Sunflower)
		measurement = measure()

	return measure()

def should_water(position):
	water_left = num_items(Items.Water)
	if water_left < 100:
		return position[1] > 25
	# return utils.distance(position, (0, 0)) > 10
	return WATER_CROP

# =================== ROLLING-UP PETAL COUNTS ===================

# rollup the set of positions for each unique petal count
# positions_and_petals: is an iterable of tuples (position, num_petals)
# returns: dictionary mapping petal counts to partitions to positions in those partitions
def aggregate_by_petals(positions_and_petals, available_drones=0):
	# petals -> partition -> position
	petal_partitions = {}

	# each thread aggregates positions found for each petal count, in one particular partition
	def aggregate_positions_per_petal_count(partition, positions_and_petals):
		positions_per_petal = {}

		# for any positions which are in this partition
		for (position, petals) in positions_and_petals:
			# if this positiosn is outside the partition, skip
			if position_to_partition[position] != partition:
				continue

			if petals in positions_per_petal:
				# insert this position in sorted order
				utils.insert_sorted(positions_per_petal[petals], position, utils.is_farther_from_origin)
			else:
				positions_per_petal[petals] = [ position ]

		return positions_per_petal

	children = {}
	for partition_i in range(len(partitions)):
		child = spawn_drone(aggregate_positions_per_petal_count, partition_i, positions_and_petals)
		children[partition_i] = child

	# merge each child's data for their partition into the larger mapping
	# petals -> position for a specific partition, becomes
	# petals -> that partition -> those positions
	for partition_i in children:
		child = children[partition_i]

		# child returns dict of positions under each petals count,
		# all for the child's partition
		positions_per_petal = wait_for(child)

		for petals in positions_per_petal:
			if petals in petal_partitions:
				petal_partitions[petals][partition_i] = positions_per_petal[petals]  
			else:
				petal_partitions[petals] = { partition_i: positions_per_petal[petals] }

	return petal_partitions

# =================== HARVESTING SUNFLOWERS ===================

# funflower_partitions is a dictionary of partition indecies, and lists of sunflowers in that partition
def harvest_sunflowers(sunflower_partitions: dict[int, list[tuple]]):
	children = set()

	# loop through partitions in partitions order, since that's farthest away to closest
	for partition_i in range(len(partitions)):
		if partition_i not in sunflower_partitions:
			continue

		child = spawn_drone(harvest_partition, sunflower_partitions[partition_i])
		children.add(child)

	for child in children:
		wait_for(child)

# sunflower_positions: a list of position tuples
def harvest_partition(sunflower_positions: list[tuple]):
	# utils.sort_by(sunflower_positions, utils.is_farther_from_origin)
	position = (0, 0)

	while len(sunflower_positions) > 0:
		nearest_neighbor = sunflower_positions[0]
		min_distance = utils.distance(nearest_neighbor, position)

		# find nearest neighbor
		for position in sunflower_positions[1:]:
			distance = utils.distance(position, (0, 0))
			if distance < min_distance:
				nearest_neighbor = position
				min_distance = distance

		drone.move_to(nearest_neighbor[0], nearest_neighbor[1])
		position = nearest_neighbor
		harvest_sunflower()
		sunflower_positions.remove(position)

	# for position in sunflower_positions:
	# 	drone.move_to(position[0], position[1])
	# 	harvest_sunflower()

def harvest_sunflower():
	if get_entity_type() != Entities.Sunflower:
		return

	if WAIT_FOR_FULLY_GROWN:
		if not can_harvest():
			(x, y) = (get_pos_x(), get_pos_y())
			quick_print('inefficient @', (x, y), ', ', utils.distance((x, y), (0, 0)))
		while not can_harvest():
			pass
	else:
		if not can_harvest():
			(x, y) = (get_pos_x(), get_pos_y())
			quick_print('missed harvest @', (x, y), ', ', utils.distance((x, y), (0, 0)))

	harvest()

def farm(should_stop=None):
	checkpoint = utils.set_checkpoint()

	initialize_farm_partitions()

	while should_stop == None or not should_stop():
		# PLANTING
		quick_print('planting sunflowers')
		checkpoint()

		positions_and_petals = plant_field()

		if should_stop != None and should_stop():
			return

		(seconds, ticks, _) = checkpoint()['since_last_check']
		drone.move_to(0, 0)
		quick_print('plant sunflowers:', seconds, 'seconds,', ticks, 'ticks')

		quick_print('aggregating petal counts')
		checkpoint()

		petal_partitions = aggregate_by_petals(positions_and_petals, max_drones() - 1)

		(seconds, ticks, _) = checkpoint()['since_last_check']
		quick_print('aggregate planting data:', seconds, 'seconds,', ticks, 'ticks')

		if should_stop != None and should_stop():
			return

		# HARVESTING 
		quick_print('harvesting sunflowers')
		checkpoint()

		for petal_count in range(15, 6, -1):
			if petal_count not in petal_partitions:
				continue

			if should_stop != None and should_stop():
				return

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
	farm()