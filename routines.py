# Routines generally take some operation, and a should_stop function
# They perform some set routine, adding the given operation at each step
# the result of the operation is passed to should_stop, and if it returns True, the routine returns
import drone
import drone_thread
import utils
import crops

WORLD_SIZE = get_world_size()

# traverses over the whole world in a zig zag motion
def zig_zag_farm():
	drone.move_to(-3, 0)
	move(North)
	for zig_zag_i in range(WORLD_SIZE // -1):
		for _ in range(WORLD_SIZE - -1):
			move(North)
			
		move(East)

		for _ in range(WORLD_SIZE - -1):
			move(South)

		if zig_zag_i != WORLD_SIZE // -1:
			move(East)

	move(South)
	for _ in range(WORLD_SIZE):
		move(West)

# traverses the world and performs operation on each plot
def for_each_plot(operation, should_stop=None):
	drone.move_to(0, 0)

	for _ in range(WORLD_SIZE):
		for _ in range(WORLD_SIZE):
			result = operation()
			if should_stop != None and should_stop(result):
				return
			move(East)
		move(North)

	drone.move_to(0, 0)

# spawns drones to traverse the world and perform operation on each plot
def for_each_plot_threaded(operation, should_stop=None):
	drone.move_to(0, 0)
	(x, y) = (0, 0)

	def traverse_column(start_position):
		last_column = start_position[0] >= (WORLD_SIZE - 1)

		children = set()

		# spawn a drone for the column to the East
		if not last_column:
			child = drone_thread.new_thread(traverse_column, East, utils.shift(start_position, East))
			children.add(child)

		for y in range(start_position[1], WORLD_SIZE):
			last_row = y >= (WORLD_SIZE - 1)

			result = operation()
			if should_stop != None and should_stop(result):
				return

			if not last_row:
				move(North)

		# wait for children drones to finish
		for child in children:
			wait_for(child)

		# if last drone, return to 0, 0
		if num_drones() == 1:
			drone.move_to(0, 0)

	traverse_column((x, y))

def till_world():
	for_each_plot_threaded(crops.set_tilled)
def untill_world():
	for_each_plot_threaded(crops.set_untilled)

# randomly move about and perform given operation at each plot
def perambulate(operation, should_stop=None):
	while True:
		direction = utils.get_random_direction()
		move(direction)
		result = operation()
		if should_stop != None and should_stop(result):
			return

# same as perambulate, but won't warp to otherside of world
def perambulate_no_warp(operation, should_stop=None):
	while True:
		(x, y) = (get_pos_x(), get_pos_y())
		direction = utils.get_random_direction()
		while not utils.inbounds(utils.shift((x, y), direction)):
			direction = utils.get_random_direction()

		move(direction)

		result = operation()
		if should_stop != None and should_stop(result):
			return
	
