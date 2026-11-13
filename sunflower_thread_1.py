import routines
import crops
import drone
import drone_thread
import utils

import partitioner

WORLD_SIZE = get_world_size()

def harvest_sunflower_partition(sunflower_positions):
	for sunflower_position in sunflower_positions:
		drone.move_to(sunflower_position[0], sunflower_position[1])
		harvest()
	
def harvest_sunflowers(sunflower_positions) -> None:
	# drone.move_to_center()
	children = set()

	available_drones = max_drones() - num_drones()
	num_partitions = min(available_drones, len(sunflower_positions))
	partitions = partitioner.front_loaded_partition(sunflower_positions, num_partitions)

	for partition in partitions:
		child = drone_thread.new_thread(harvest_sunflower_partition, None, partition)
		children.add(child)
			
	drone_thread.wait_for_children(children)

def plant_and_measure():
	crops.handle_sunflower()
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

		measurement = plant_and_measure()
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

def farm(should_stop: function=None):
	while should_stop == None or not should_stop():
		drone.move_to(0, 0)
		(x, y) = (0, 0)
			
		measurements = plant_column((x, y))
		(x, y) = (get_pos_x(), get_pos_y())
		for measurement in range(15, 6, -1):
			if measurement in measurements:
				harvest_sunflowers(measurements[measurement])
	
if __name__ == '__main__':
	clear()
	farm()