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
#			# estimated number of ticks to harvest these sunflowers
#			# starting at partition's zero
#			'tick_estimate': 5323
# 		}
#	}
def plant_partition(partition_id: int) -> dict:
	partition = partitions[partition_id]
	drone.move_to(partition['zero'][0], partition['zero'][1])

	path = partition['path']

	# tracks sub path for each petal count
	petal_paths = {}
	# initizlize 
	for petals in range(MIN_PETALS_ALLOWED, MAX_PETALS + 1):
		petal_paths[petals] = {
			# all petals' paths start where the partition's path starts
			'path': [path[0]],
			# for overhead in harvest_partition(), that's per petal-count instead of per sunflower
			'tick_estimate': 4
		}

	# plant and measure paths
	for step in path:
		drone.move_to(step[0], step[1])

		# plant and measure sunflower
		petals = plant_sunflower(step)

		# update tracking
		if petals != None:
			petal_paths[petals]['path'].append(step)

	for petals in range(MIN_PETALS_ALLOWED, MAX_PETALS + 1):
		petal_path = petal_paths[petals]['path']
		tick_estimate = quote_harvest_cost(petal_path)
		petal_paths[petals]['tick_estimate'] = tick_estimate

	return petal_paths


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

# petals_max_ticks is the estimated max ticks it'll take for each petal to be fully harvested
def spawn_harvesters(petals_max_ticks: dict[int, int], spawn_partitions=partitions):
	num_spawn_partitions = len(spawn_partitions)
	half_partitions_pivot = num_spawn_partitions // 2

	if num_spawn_partitions == 0:
		return utils.error('no partitions given to spawn harvesters for')

	# harvest the partition yourself
	if num_spawn_partitions == 1:
		partition = spawn_partitions[1]
		harvest_partition(partition, petals_max_ticks)

	child = spawn_harvesters(spawn_partitions[:half_partitions_pivot])
	spawn_harvesters(spawn_partitions[half_partitions_pivot:])

	wait_for(child)

def harvest_partition(partition_i, petals_max_ticks: dict[int, int]):
	# TODO drones spawned with sync ticks passed in
	# TODO on specific ticks, drones harvest measurment at same time

	partition = partitions[partition_i]
	partition_zero = partition['zero']
	drone.move_to(partition_zero[0], partition_zero[1])

	# each tick is tracked within this loop to sync threads
	for petals in range(MAX_PETALS, MIN_PETALS_ALLOWED - 1, - 1):
		start = get_tick_count()

		# 3 ticks
		petal_path = partitions[partition_i]['petal_paths'][petals]
		# 1 tick
		path = petal_path['path']
		# 1 tick
		num_steps = len(path)

		# 0 tick
		# every partition starts on partition_zero
		previous_step = partition_zero 
		# 2 ticks
		for i in range(1, num_steps):
			# 1 tick
			step = path[i]

			# 10 base, 7 / axis moved, 200 / step
			drone.precise_move_to(previous_step, step)

			# 0 ticks
			previous_step = step
			# 200 ticks
			harvest()

		# 1 tick
		last_step = path[-1]
		# 10 base, 7 / axis moved, 200 / step
		drone.precise_move_to(last_step, partition_zero)

		end = get_tick_count()
		quick_print(
			'partition', partition_i,
			'petals', petals,
			'number of steps', len(path),
			'estimate', petals_max_ticks[petals],
			'got', end-start
		)


def quote_harvest_cost(path):
	# overhead cost of harvest_partition()
	tick_cost = 8

	prev_step = path[0]
	for step in path[1:]:
		precise_move_quote = drone.quote_precise_move_cost(prev_step, step)
		tick_cost += precise_move_quote
		# harvesting and logic in harvest_partition()
		tick_cost += 201

		prev_step = step

	# overhead of move back to partition zero
	tick_cost += drone.quote_precise_move_cost(path[-1], path[0])

	return tick_cost

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
		# reserve your partition to do after child spawned
		if partition_i == your_partition:
			continue

		# TODO tree-spawn planters
		child = spawn_drone(plant_partition, partition_i)
		children[partition_i] = child

	your_petal_paths = plant_partition(your_partition)
	partitions[your_partition]['petal_paths'] = your_petal_paths

	petals_max_tick_estimate = {}
	for petals in range(MIN_PETALS_ALLOWED, MAX_PETALS + 1):
		petals_max_tick_estimate[petals] = partitions[your_partition]['tick_estimate']

	# return children & aggregate max ticks / petals
	for child_partition in children:
		child = children[child_partition]
		child_results = wait_for(child)
		partitions[child_partition]['petal_paths'] = child_results

		for petals in child_results:
			petals_tick_estimate = child_results[petals]['tick_estimate']
			max_tick_estimate = petals_max_tick_estimate[petals]
			if petals_tick_estimate > max_tick_estimate:
				petals_max_tick_estimate[petals] = petals_tick_estimate

	spawn_harvesters(petals_max_tick_estimate)

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
# returns: list of tuples of path length, total path distance, and ticks that path took to harvest
def test_harvest_ticks() -> list[tuple]:
	global partitions

	quick_print('---')

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

	# manually create only partition, instead of having to initialize_farm_partitions()
	partitions.append(partition)
	partition_id = 0

	petal_paths = plant_partition(partition_id)
	partition['petal_paths'] = petal_paths

	petals_max_ticks = {}
	for petals in petal_paths:
		petals_max_ticks[petals] = petal_paths[petals]['tick_estimate']

	harvest_partition(partition_id, petals_max_ticks)

# def get_average_harvest_ticks_per_distance():
# 	num_runs = 20
# 
# 	# num_ticks / distance for each petal-harvest run
# 	all_results = []
# 
# 	for _ in range(num_runs):
# 		results = test_harvest_ticks()
# 		for result in results:
# 			path_length = results[0]
# 			distance = result[1]
# 			num_ticks = result[2]
# 			rate = num_ticks / distance
# 
# 			all_results.append(rate)
# 
# 
# 	num_results = len(all_results)
# 	mean = utils.avg_list(all_results)
# 	diffs_squared = []
# 	for result in all_results:
# 		diff = abs(result - mean)
# 		diff_squared = diff**2
# 		diffs_squared.append(diff_squared)
# 	sum_diffs_squared = utils.sum_list(diffs_squared)
# 	standard_deviation = (sum_diffs_squared / num_results)**0.5
# 
# 	quick_print('mean', mean, 'ticks / step')
# 	quick_print('standard deviation', standard_deviation, 'ticks / step')

if __name__ == '__main__':
	clear()
	# farm()

	test_harvest_ticks()
	# get_average_harvest_ticks_per_distance()
