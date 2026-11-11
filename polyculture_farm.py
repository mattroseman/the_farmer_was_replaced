import utils
import drone
import crops

WORLD_SIZE = get_world_size()

farm_state = utils.get_farm_state_matrix()
plots_queue = []

# run through the plots_queue to harvest all companioned props
# and clear out the queue
# Hay : 32464 units, 6492.8 / minute
# Wood : 79904 units, 15980.8 / minute
# Carrot : 13904 units, 2780.8 / minute
def harvest_plots_queue():
	global plots_queue
	global farm_state
	
	for (x, y) in plots_queue:
		drone.move_to(x, y)
		
		crop = get_entity_type()
		crops.get_crop_handler(crop)()
		
		farm_state[y][x] = get_entity_type()
		
	plots_queue = []

# harvest plots using nearest neighbor algorithm for travelling salesman
# Hay : 3664 units, 7328 / minute
# Wood : 6656 units, 13312 / minute
# Carrot : 960 units, 1920 / minute
def harvest_plots_queue_nn():
	global plots_queue
	global farm_state

	# do nothing if there is no queue
	if len(plots_queue) == 0:
		return
	
	x = get_pos_x()
	y = get_pos_y()
	next_plot = None

	# initialize to a max everything will be less than
	min_dist = WORLD_SIZE * 2
	# find closest plot in queue
	for i in range(len(plots_queue)):
		plot = plots_queue[i]
		dist = utils.distance((x, y), plot)
		if dist < min_dist:
			min_dist = dist
			next_plot = plot
			
	drone.move_to(next_plot[0], next_plot[1])
	crop = get_entity_type()
	crops.get_crop_handler(crop)()
		
	plots_queue.remove(next_plot)
	
	harvest_plots_queue_nn()

def farm(should_stop=None):
	global plots_queue
	global farm_state
	

	quick_print('Running Polyculture Farm')
	
	if get_entity_type() in [Entities.Grass, Entities.Carrot, Entities.Bush, Entities.Tree]:
		crop = get_entity_type()
	else:
		crop = Entities.Grass

	while should_stop == None or not should_stop():
		x = get_pos_x()
		y = get_pos_y()
		
		# process crop
		crops.get_crop_handler(crop)()
		
		# update farm state
		farm_state[y][x] = crop
		
		# check companion for next crop
		companion_crop, (companion_x, companion_y) = get_companion()
		
		# if the companion chain has a cycle, clear it out
		if (companion_x, companion_y) in plots_queue:
			# DEBUG
			change_hat(Hats.Traffic_Cone)
			
			harvest_plots_queue()
			# harvest_plots_queue_nn()
			
			# DEBUG
			change_hat(Hats.Straw_Hat)
			
		# update plots_queue
		plots_queue.append((x, y))
		
		drone.move_to(companion_x, companion_y)
		crop = companion_crop

if __name__ == '__main__':
	clear()
	farm()
	# utils.performance_test_farm(farm, 5 * 60)