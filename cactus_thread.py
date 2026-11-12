set_world_size(10)

import crops
import routines
import utils

WORLD_SIZE = get_world_size()

# will get set after crops planted
farm_state = utils.get_farm_state_matrix()

def farm():
	global plot_measurements

	def plant_and_measure(position):
		crops.handle_cactus()
		size = measure()
		return measure()
		
	plot_measurements = routines.for_each_plot_threaded(plant_and_measure)
	# convert dict of plot measurements to a farm-state matrix for sorting
	for plot in plot_measurements:
		plot_measurement = plot_measurements[plot]
		farm_state[plot[1]][plot[0]] = plot_measurement

	(x, y) = (get_pos_x(), get_pos_y())

	# send out a drone to sort each row
	for row in range(WORLD_SIZE):
		drone_thread.new_thread(sort_row, )
	# TODO send out a drone to sort each column
	# TODO harvest

if __name__ == '__main__':
	clear()
	farm()