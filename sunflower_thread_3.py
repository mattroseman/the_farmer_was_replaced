import crops
import drone
import drone_thread
import utils
import routines

import partitioner
import cache

WORLD_SIZE = get_world_size()
# set to lower than 15 to limit planting to sunflowers with this number of petals or less
# increases planting time, but decreases harvesting time
MAX_SUNFLOWER_PETALS = 10

currently_harvesting_measurement = None

partitions = []
# mapping of position to the index of the corresponding partition in partitions
position_to_partition = {}

def initialize_farm_partitions():
	global partitions
	global position_to_partition 

	# use precomputed values when the world matches what the cache was built for
	if WORLD_SIZE == 32 and max_drones() == 32:
		partitions = cache.WORLD_PARTITIONS
		position_to_partition = cache.WORLD_POSITION_TO_PARTITION_MAP
		return
	# leave this uncommented while the above cache is commented
	# print('initializing farm partitions')

	# one main drone remains and spawns all children
	num_partitions = min(max_drones() - 1, WORLD_SIZE*WORLD_SIZE)

	partitions = partitioner.partition_region((0, 0), WORLD_SIZE, WORLD_SIZE, num_partitions)

	# sort partitions so the farthest partitions are first
	def partition_comparer(a, b):
		a_center = (a['zero'][0] + a['width'] // 2, a['zero'][1] + a['height'] // 2)
		b_center = (b['zero'][0] + b['width'] // 2, b['zero'][1] + b['height'] // 2)
		a_dist = utils.distance(a_center, (0, 0))
		b_dist = utils.distance(b_center, (0, 0))

		# favor the farther-away partition, i.e. closer partitions sort later
		return a_dist < b_dist
	utils.sort_by(partitions, partition_comparer)

	position_to_partition = {}
	for partition_i in range(num_partitions):
		partition = partitions[partition_i]
		for x in range(partition['zero'][0], partition['zero'][0] + partition['width']):
			for y in range(partition['zero'][1], partition['zero'][1] + partition['height']):
				position_to_partition[(x, y)] = partition_i

def harvest_sunflowers(sunflower_positions, reverse_order=False) -> None:
	# sort so closer to origin sunflowers are first
	if not reverse_order:
		utils.sort_by(sunflower_positions, utils.is_farther_from_origin)
	else:
		utils.sort_by(sunflower_positions, utils.is_closer_to_origin)

	for sunflower_position in sunflower_positions:
		drone.move_to(sunflower_position[0], sunflower_position[1])

		# wait for sunflower to finish growing
		while get_entity_type() == Entities.Sunflower and not can_harvest():
			pass

		harvest()

# groups the set of (sunflower_position, measurement) tuples from routines.fast_plant by measurement
# returns a dict of measurement to the set of sunflower positions with that measurement
def group_positions_by_measurement(planted):
	measurement_positions = {}
	for planted_sunflower in planted:
		sunflower_position = planted_sunflower[0]
		measurement = planted_sunflower[1]

		if measurement in measurement_positions:
			measurement_positions[measurement].add(sunflower_position)
		else:
			measurement_positions[measurement] = { sunflower_position }

	return measurement_positions

# takes a dict of measurments and the positions found with that measurement
# and converts to a dict of measurements to partitions to positions
# {
#   15: {
#      partition_1_index: [position1, position2, ...],
#      partition_2_index: [position4, position5, ...],
#   },
#   14: {...},
#   ...
# }
# so measurement_partitions[15][0] gets the sunflowers with measurement 15 found in partition 0
def convert_measurements_to_measurement_partitions(measurements):
	measurement_partitions = {}

	for measurement in measurements:
		measurement_positions = measurements[measurement]
		partitions_for_measurement = {}

		# for each position found with this measurement
		for position in measurement_positions:
			# add position to corresponding partition under same measurement
			partition_i = position_to_partition[position]
			if partition_i in partitions_for_measurement:
				partitions_for_measurement[partition_i].append(position)
			else:
				partitions_for_measurement[partition_i] = [position]

		measurement_partitions[measurement] = partitions_for_measurement

	return measurement_partitions

# aggregates a set of tuples (position, measurement)
# recording a sunflower measurement at that position
# into the organized dict of measurement -> partition -> position
def aggregate_by_partition(position_measurements: set[tuple]): 
	aggregate_dict = {}

	for position_measurement in position_measurements:
		(position, measurement) = position_measurement
		partition = position_to_partition[position]

		if measurement not in aggregate_dict:
			aggregate_dict[measurement] = { partition: [ position ] }
		elif partition not in aggregate_dict[measurement]:
			aggregate_dict[measurement][partition] = [ position ]
		else:
			aggregate_dict[measurement][partition].append(position)

	return aggregate_dict

def farm(should_stop: function=None):
	global currently_harvesting_measurement

	initialize_farm_partitions()

	def plant_and_measure():
		crops.handle_sunflower()
		measurement = measure()
		# while measurement > MAX_SUNFLOWER_PETALS:
		# 	harvest()
		# 	crops.handle_sunflower(True)
		# 	measurement = measure()

		return measurement

	while should_stop == None or not should_stop():
		drone.move_to(0, 0)
		(x, y) = (0, 0)

		# when fast planting, the first column drones turn Westward and warp over to finish the last columns faster
		# this tunes where the first drone starts turning
		start_bend_y = WORLD_SIZE*0.80 // 1
		position_measurements = routines.fast_plant(
			Entities.Sunflower,
			plant_and_measure,
			start_bend_y
		)
		drone.move_to(0, 0)

		# for each position and measurement, aggregate into a nested dict of measurement -> partitions -> positions
		measurement_partitions = aggregate_by_partition(position_measurements)
		# measurement_positions = group_positions_by_measurement(position_measurements)
		# measurement_partitions = convert_measurements_to_measurement_partitions(measurement_positions)

		for currently_harvesting_measurement in range(15, 6, -1):
			if currently_harvesting_measurement not in measurement_partitions:
				continue

			num_partitions_for_measurement = len(measurement_partitions[currently_harvesting_measurement])
			partitions_left = num_partitions_for_measurement
			children = []

			# make sure to execute partitions in order for farther away partitions to be done earlier
			for partition_i in range(len(partitions)):
				if partition_i in measurement_partitions[currently_harvesting_measurement]:
					sunflowers = measurement_partitions[currently_harvesting_measurement][partition_i]

					child = spawn_drone(harvest_sunflowers, sunflowers)
					children.append(child)

					# if children have already returned, send out an extra drone
					drones_free = max_drones() - num_drones() - partitions_left
					if drones_free > 0:
						child = spawn_drone(harvest_sunflowers, sunflowers, True)
						children.append(child)

					partitions_left -= 1

			drone_thread.wait_for_children(children)
	
if __name__ == '__main__':
	clear()
	farm()