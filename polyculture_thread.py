import utils
import drone
import drone_thread
import crops

WORLD_SIZE = get_world_size()

# gets the crop on the current plot, defaulting to grass if the plot
# is empty (e.g. another drone is mid-harvest here) or isn't a polyculture crop
def get_current_crop():
	crop = get_entity_type()
	if crop not in crops.CROP_HANDLERS:
		crop = Entities.Grass

	return crop

# run through the plots_queue to harvest all companioned crops
# another drone may have planted over a plot since it was queued, so whatever
# crop is there now is the one that's handled
def harvest_plots_queue(plots_queue):
	for (x, y) in plots_queue:
		drone.move_to(x, y)

		crop = get_current_crop()
		crops.get_crop_handler(crop)()

# follows the chain of companions, starting from the current plot
# plots_queue is local, so each drone tracks only its own chain
def companion_loop(should_stop=None):
	plots_queue = []

	crop = get_current_crop()

	while should_stop == None or not should_stop():
		x = get_pos_x()
		y = get_pos_y()

		# process crop
		crops.get_crop_handler(crop)()

		# check companion for next crop
		companion = get_companion()

		# no companion means another drone harvested this plot out from under us
		# so replant whatever is here now
		if companion == None:
			crop = get_current_crop()
			continue

		companion_crop, (companion_x, companion_y) = companion

		# if the companion chain has a cycle, clear it out
		if (companion_x, companion_y) in plots_queue:
			harvest_plots_queue(plots_queue)
			plots_queue = []

		# update plots_queue
		plots_queue.append((x, y))

		drone.move_to(companion_x, companion_y)
		crop = companion_crop

	# don't leave this drone's chain unharvested
	harvest_plots_queue(plots_queue)

# moves to a random plot before starting the companion loop
# so the drones start out spread across the world
def spread_out_and_farm(should_stop=None):
	(x, y) = utils.get_random_plot()
	drone.move_to(x, y)

	companion_loop(should_stop)

def farm(should_stop=None):
	quick_print('Running Polyculture Thread Farm')

	children = set()

	# spawn every available drone, saving this drone to run a loop of its own
	available_drones = max_drones() - num_drones()
	for _ in range(available_drones):
		child = drone_thread.new_thread(spread_out_and_farm, None, should_stop)
		children.add(child)

	spread_out_and_farm(should_stop)

	drone_thread.wait_for_children(children)

if __name__ == '__main__':
	clear()
	farm()
	# utils.performance_test_farm(farm, 5 * 60)
