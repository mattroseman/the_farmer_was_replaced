import utils
import partitioner
import drone
import paths

WORLD_SIZE = get_world_size()

WATER_CROP = True

# determines behavior, with not-fully-grown crops
# 'wait': 			wait for the sunflower to fully grow 
# 'skip_then_wait': continue harvesting partition and come back, then wait
# 'ignore': 		harvest anyway, and lost the power
HARVEST_MODE = 'skip_then_wait'
# NOTE 'ignore' works well in leaderboard runs, with limited water
# 'skip_then_wait' works best with plenty of water available

# limit range of measurements during planting
MIN_PETALS_ALLOWED = 12
# sunflowers have 7-15 petals
MIN_PETALS = 7
MAX_PETALS = 15

NUM_DUMMY_PLOTS = 10

# [{
# 	'zero': (0, 0),
#	'width': 5,
# 	'height': 5,
#	'path': [(0,0), (0,1), ...]
# }]
partitions = []
# mapping of position to the index of the corresponding partition in partitions
position_to_partition = {}

dummy_plots = set()

# =================== PARTITIONING FARM ===================

def initialize_farm_partitions():
	global partitions
	global position_to_partition

	# already been built
	if len(partitions) > 0 and len(position_to_partition) > 0:
		return

	# one main drone remains and spawns all children
	# or number of plots, if that's smaller
	num_partitions = min(max_drones(), WORLD_SIZE*WORLD_SIZE)

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

	# construct mapping of position tuples to partition indecies
	# for quick lookup
	position_to_partition = {}
	for partition_i in range(num_partitions):
		partition = partitions[partition_i]
		for x in range(partition['zero'][0], partition['zero'][0] + partition['width']):
			for y in range(partition['zero'][1], partition['zero'][1] + partition['height']):
				position_to_partition[(x, y)] = partition_i

	# construct paths for each partition
	# TODO move this into the partitioner.partition_region, maybe as additional_data_callback,
	# 	so this can be done in parallel 
	for partition_i in range(num_partitions):
		partition = partitions[partition_i]
		partitions[partition_i]['path'] = paths.build_hamiltonian_path(
			partition['zero'],
			partition['width'],
			partition['height']
		)

def setup_dummy_plots():
	global dummy_plots

	dummy_plots = set()

	# put dummy plots in last two columns to be planted
	left_plots_x = WORLD_SIZE // 2
	num_rows = -(-NUM_DUMMY_PLOTS // 2)
	dummy_plot_start_y = (WORLD_SIZE // 2) - (num_rows // 2)

	for i in range(NUM_DUMMY_PLOTS):
		x = left_plots_x + (i % 2)
		y = dummy_plot_start_y + (i // 2)
		dummy_plots.add((x, y))

	children = set()
	for dummy_plot in dummy_plots:
		child = spawn_drone(plant_dummy_sunflower, dummy_plot)
		children.add(child)

	for child in children:
		wait_for(child)

	return dummy_plots

# =================== PLANTING SUNFLOWERS ===================

# returns: dict of path data for each petal count
# 	{
#		# for sunflowers with 7 petals
#		7: {
#			# path of those 7-petal sunflowers in this partition
#			'path': [(0, 0), (0, 1), ...],
#			# distance to travel path, in order
#			'distance': 23
# 		}
#	}
def plant_partition(partition_id: int) -> dict:
	partition = partitions[partition_id]
	drone.move_to(partition['zero'][0], partition['zero'][1])

	path = partition['path']

	# tracks sub path for each petal count
	petals_paths = {}
	# initizlize 
	for petals in range(MIN_PETALS_ALLOWED, MAX_PETALS + 1):
		petals_paths[petals] = {
			# all petals' paths start where the partition's path starts
			'path': [path[0]],
			'distance': 0
		}

	# plant and measure paths
	for step in path:
		drone.move_to(step[0], step[1])

		# plant and measure sunflower
		petals = plant_sunflower(step)

		# update tracking
		if petals != None:
			last_step = petals_paths[petals]['path'][-1]
			petals_paths[petals]['path'].append(step)
			petals_paths[petals]['distance'] += utils.distance(last_step, step)

	return petals_paths


# returns: measurement of not-planted sunflower or None if dummy plot
def plant_sunflower(position) -> int | None:
	if get_ground_type() != Grounds.Soil:
		till()

	# once dummy plots are planted, ignore them
	if position in dummy_plots:
		if get_entity_type() != Entities.Sunflower:
			plant_dummy_sunflower(position)
		return None

	if should_water(position):
		use_item(Items.Water)

	plant(Entities.Sunflower)

	measurement = measure()
	while measurement < MIN_PETALS_ALLOWED:
		harvest()
		plant(Entities.Sunflower)
		measurement = measure()

	return measurement

def plant_dummy_sunflower(position):
	drone.move_to(position[0], position[1])

	if get_ground_type() != Grounds.Soil:
		till()

	plant(Entities.Sunflower)
	# dummy sunflowers have to be less than all others
	while measure() >= MIN_PETALS_ALLOWED:
		harvest()
		plant(Entities.Sunflower)

def should_water(position):
	if not WATER_CROP:
		return False

	if get_water() >= 0.5:
		return False

	water_left = num_items(Items.Water)
	if water_left <= 20:
		return False
	if water_left < 1000:
		return position[1] > WORLD_SIZE // 2 

	return True

# =================== HARVESTING SUNFLOWERS ===================

# petals_max_distance is max distance traversed by any partition, for each petal count's harvest
def spawn_harvesters(petals_max_distance: dict[int, int], spawn_partitions=partitions):
	num_spawn_partitions = len(spawn_partitions)
	half_partitions_pivot = num_spawn_partitions // 2

	if num_spawn_partitions == 0:
		return utils.error('no partitions given to spawn harvesters for')

	# harvest the partition yourself
	if num_spawn_partitions == 1:
		partition = spawn_partitions[1]
		harvest_partition(partition, petals_max_distance)

	child = spawn_harvesters(spawn_partitions[:half_partitions_pivot])
	spawn_harvesters(spawn_partitions[half_partitions_pivot:])

	wait_for(child)

def harvest_partition(partition, petals_max_distance: dict[int, int]):
	# TODO drones spawned with sync ticks passed in
	# TODO on specific ticks, drones harvest measurment at same time

	for petals in range(MAX_PETALS, MIN_PETALS_ALLOWED - 1, - 1):
		petal_path = partitions[partition]['petal_paths'][petals]

		quick_print('petal_path length: ', len(petal_path))

		for step in petal_path:
			drone.move_to(step[0], step[1])
			harvest()


# =================== CONTROL ===================

def farm_loop(should_stop=None):
	global partitions

	# tracking
	loop_checkpoint = utils.set_checkpoint()

	drone.move_to(0, 0)
	position = (0, 0)
	your_partition = position_to_partition[position]

	children = {}

	# plant partitions
	for partition_i in range(len(partitions)):
		partition = partitions[partition_i]
		# reserve your partition to do after child spawned
		if partition == your_partition:
			continue

		# TODO tree-spawn planters
		child = spawn_drone(plant_partition, partition)
		children[partition_i] = child

	results = { your_partition: plant_partition(your_partition) }
	partitions[your_partition]['petal_paths'] = results

	petals_max_distances = {}
	for petals in min(MIN_PETALS_ALLOWED, MAX_PETALS + 1):
		petals_max_distances[petals] = partitions[your_partition]['distance']

	# return children & aggregate max ticks / petals
	for child_partition in children:
		child = children[child_partition]
		child_results = wait_for(child)
		partitions[child_partition]['petal_paths'] = child_results

		for petals in child_results:
			petals_distance = child_results[petals]['distance']
			petals_max_distance = petals_max_distances[petals]
			if petals_distance > petals_max_distance:
				petals_max_distance[petals] = petals_distance

	spawn_harvesters(petals_max_distance)

	# tracking
	(seconds, ticks, _) = loop_checkpoint()['since_last_check']
	quick_print('harvest sunflowers:', seconds, 'seconds,', ticks, 'ticks')

	# tracking
	(seconds, _, item_diff) = loop_checkpoint()['since_checkpoint']
	rate = item_diff[Items.Power] / seconds
	quick_print('loop seconds:', seconds, 'seconds')
	quick_print('loop rate:', rate, 'power/s')


def farm(should_stop=None):
	global dummy_plots

	# tracking
	quick_print('---')
	run_checkpoint = utils.set_checkpoint()

	dummy_plot_child = spawn_drone(setup_dummy_plots)
	initialize_farm_partitions()
	dummy_plots = wait_for(dummy_plot_child)

	while should_stop == None or not should_stop():
		farm_loop(should_stop)

		# tracking
		(seconds, _, item_diff) = run_checkpoint()['since_checkpoint']
		rate = item_diff[Items.Power] / seconds
		quick_print('total rate:', rate, 'power/s')

# ------------------------------
# measure harvest ticks
# ------------------------------

# this function is to run a drone through a mock harvest, and print the tick counts for actions
# this data can then invorm the sync schedule drones are put on, based on number of harvests they need to do
def test_harvest_ticks():
	global partitions

	initialize_farm_partitions()

	# 32 partitions, on 32x32 world, average partition size of 32
	partition =  {
		'zero': (1, 1),
		'width': 8,
		'height': 4
	}
	path = paths.build_hamiltonian_path(
		partition['zero'],
		partition['width'],
		partition['height']
	)
	partition['path'] = path

	partitions[0] = partition
	partition_id = 0

	plant_partition(partition_id)

if __name__ == '__main__':
	clear()
	# farm()

	test_harvest_ticks()
