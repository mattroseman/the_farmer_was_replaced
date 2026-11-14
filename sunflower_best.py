import crops
import drone
import drone_thread
import utils

import partitioner
import cache

WORLD_SIZE = get_world_size()
# set to lower than 15 to limit planting to sunflowers with this number of petals or less
# increases planting time, but decreases harvesting time
MAX_SUNFLOWER_PETALS = 10

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

	# one main drone remains and spawns all children
	num_partitions = min(max_drones() - 1, WORLD_SIZE*WORLD_SIZE)

	partitions = partitioner.partition_region((0, 0), WORLD_SIZE, WORLD_SIZE, num_partitions)

	# sort partitions so the farthest partitions are first
	def partition_comparer(a, b):
		a_center = (a['zero'][0] + a['width'] // 2, a['zero'][1] + a['height'] // 2)
		b_center = (b['zero'][0] + b['width'] // 2, b['zero'][1] + b['height'] // 2)
		a_dist = utils.distance(a_center, (0, 0))
		b_dist = utils.distance(b_center, (0, 0))

		# favor the farther-away partition, i.e. sort it earlier
		return a_dist > b_dist
	utils.sort_by(partitions, False, partition_comparer)

	position_to_partition = {}
	for partition_i in range(num_partitions):
		partition = partitions[partition_i]
		for x in range(partition['zero'][0], partition['zero'][0] + partition['width']):
			for y in range(partition['zero'][1], partition['zero'][1] + partition['height']):
				position_to_partition[(x, y)] = partition_i

def harvest_sunflowers(sunflower_positions) -> None:
	for sunflower_position in sunflower_positions:
		drone.move_to(sunflower_position[0], sunflower_position[1])
		
		if not can_harvest():
			print('inefficient')
		while not can_harvest() and get_entity_type() == Entities.Sunflower:
			pass
		
		harvest()

def plant_and_measure(should_water=False):
	crops.handle_sunflower()
	measurement = measure()
	while measurement > MAX_SUNFLOWER_PETALS:
		harvest()
		crops.handle_sunflower(should_water)
		measurement = measure()
	return measurement

def plant_column(start_position: tuple[int, int]) -> dict[int, list[tuple[int, int]]]:
	position = start_position
	last_column = start_position[0] >= (WORLD_SIZE - 1)
	measurements = {}

	children = set()

	# spawn a drone for the column to the East
	if not last_column:
		child = drone_thread.new_thread(plant_column, East, utils.shift(start_position, East))
		children.add(child)

	for y in range(start_position[1], WORLD_SIZE):
		last_row = y >= (WORLD_SIZE - 1)

		should_water = utils.distance_no_wrap(position, (0, 0)) >= 48
		measurement = plant_and_measure(should_water)
		if measurement in measurements:
			measurements[measurement].append(position)
		else:
			measurements[measurement] = [position]
			
		if not last_row:
			move(North)
			position = utils.shift(position, North)

	# wait for children drones to finish
	for child in children:
		child_measurements = wait_for(child)
		for measurement in child_measurements:
			# combine the list of points this child has for this measurement, with this drone's list
			if measurement in measurements:
				measurements[measurement] = measurements[measurement] + child_measurements[measurement]
			else:
				measurements[measurement] = child_measurements[measurement]
				
	# if last drone, return to 0, 0
	if num_drones() == 1:
		drone.move_to(0, 0)
			
	return measurements

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

def farm(should_stop: function=None):
	initialize_farm_partitions()

	while should_stop == None or not should_stop():
		drone.move_to(0, 0)
		(x, y) = (0, 0)
			
		measurements = plant_column((x, y))
		measurement_partitions = convert_measurements_to_measurement_partitions(measurements)

		for measurement in range(15, 6, -1):
			children = set()

			if measurement in measurement_partitions:
				# make sure to execute partitions in order for farther away partitions to be done earlier
				for partition_i in range(len(partitions)):
					if partition_i in measurement_partitions[measurement]:
						sunflowers = measurement_partitions[measurement][partition_i]
						child = drone_thread.new_thread(harvest_sunflowers, None, sunflowers)
						children.add(child)

			drone_thread.wait_for_children(children)
	
if __name__ == '__main__':
	clear()
	farm()