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

# moves the drone in a looping zig zag within the area
# encompassed by coordinates bottom_left and top_right (inclusive both)
# bottom_left[0] <= x <= top_right[0]
# bottom_left[1] <= y <= top_right[1]
def zig_zag_area(bottom_left, top_right, operation: function, callback: function=None, row_callback: function=None):
	num_rows = top_right[1] - bottom_left[1] + 1
	area_width = top_right[0] - bottom_left[0] + 1
	bottom_right = (top_right[0], bottom_left[1])
	top_left = (bottom_left[0], top_right[1])

	position = (get_pos_x(), get_pos_y())
	closest_corner = None
	closest_distance = None
	for corner in [bottom_left, bottom_right, top_right, top_left]:
		distance = utils.distance(position, corner)
		if closest_distance == None or distance < closest_distance:
			closest_corner = corner
			closest_distance = distance

	ascending = closest_corner == bottom_left or closest_corner == bottom_right

	drone.move_to(closest_corner[0], closest_corner[1])

	on_a_zig = [closest_corner == bottom_left or closest_corner == top_left]
	def zig():
		results = []

		result = operation()
		if callback != None:
			callback(result)
		results.append(result)
		for i in range(area_width - 1):
			move(East)
			result = operation()
			if callback != None:
				callback(result)
			results.append(result)

		return results
	def zag():
		results = []

		result = operation()
		if callback != None:
			callback(result)
		results.append(result)
		for i in range(area_width - 1):
			move(West)
			result = operation()
			if callback != None:
				callback(result)
			results.append(result)

		return results
	def zig_or_zag():
		if on_a_zig[0]:
			results = zig()
			if row_callback != None:
				row_callback(results)
			on_a_zig[0] = False
		else:
			results = zag()
			if row_callback != None:
				row_callback(results)
			on_a_zig[0] = True

	zig_or_zag()

	for _ in range(num_rows - 1):
		if ascending:
			move(North)
		else:
			move(South)
		zig_or_zag()

	# loop back to where you started
	for _ in range(num_rows-1):
		if ascending:
			move(South)
		else:
			move(North)

# traverses the world and performs operation on each plot
# returns a dictionary of each plot's result
def for_each_plot(operation: function, should_stop: function=None) -> dict[tuple, any]:
	drone.move_to(0, 0)
	position = (0, 0)

	results = {} 

	for _ in range(WORLD_SIZE):
		for _ in range(WORLD_SIZE):
			result = operation(position)
			results[position] = result

			if should_stop != None and should_stop(result):
				return results

			move(East)
			position = utils.shift(position, East)
		move(North)
		position = utils.shift(position, North)

	drone.move_to(0, 0)
	position = (0, 0)

	return results

# spawns drones to traverse the world and perform operation on each plot
# operation(position) is expected to take one arg, the position the drone is on
# should_stop(result) is expected to take one arg, the result of the operation, and return True if the drone should stop
# return {(0, 0): measurement, (0, 1): measurement,...} is dict of positions visited and measurements taken
def for_each_plot_threaded(
		operation: function,
		should_stop: function = None,
	) -> any | None:
	drone.move_to(0, 0)
	(x, y) = (0, 0)
	
	def traverse_column(start_position):
		position = start_position
		last_column = start_position[0] >= (WORLD_SIZE - 1)
		
		results = {}
		children = set()

		# spawn a drone for the column to the East
		if not last_column:
			child = drone_thread.new_thread(traverse_column, East, utils.shift(position, East))
			children.add(child)

		for y in range(start_position[1], WORLD_SIZE):
			last_row = y >= (WORLD_SIZE - 1)

			result = operation(position)
			results[position] = result

			if should_stop != None and should_stop(result):
				return results

			if not last_row:
				move(North)
				position = utils.shift(position, North)

		# wait for children drones to finish
		for child in children:
			child_results = wait_for(child)

			# copy over the results for each position the child visited
			for child_position in child_results:
				results[child_position] = child_results[child_position]

		# if last drone, return to 0, 0
		if num_drones() == 1:
			drone.move_to(0, 0)

		return results

	results = traverse_column((x, y))
	return results

# performs the given operation for each column, dispatching drones
# assume drone starts at position y = 0
# should_stop is passed to the operation function
def for_each_column_threaded(operation: function, should_stop: function=None):
	drone.move_to(0, 0)
	position = [(0, 0)]

	# wrapper around operation to first spawn the drone for the next column (if there is one)
	def spawn_next_drone_then_do():
		position[0] = utils.shift(position[0], East)
		last_column = position[0][0] == WORLD_SIZE - 1

		if not last_column:
			drone_thread.new_thread(spawn_next_drone_then_do, East)

		operation(should_stop)

	drone_thread.new_thread(spawn_next_drone_then_do, East)

	operation(should_stop)


def till_world():
	def set_tilled_wrapper(position):
		crops.set_tilled()
	for_each_plot_threaded(set_tilled_wrapper)
def untill_world():
	def set_untilled_wrapper(position):
		crops.set_untilled
	for_each_plot_threaded(set_untilled_wrapper)

# randomly move about and perform given operation at each plot
def perambulate(operation, should_stop=None):
	while True:
		direction = utils.get_random_direction()
		move(direction)
		result = operation()
		if should_stop != None and should_stop(result):
			return

# same as perambulate, but won't warp to otherside of world
def perambulate_no_warp(operation: function, should_stop: function=None) -> None:
	while True:
		(x, y) = (get_pos_x(), get_pos_y())
		direction = utils.get_random_direction()
		while not utils.inbounds(utils.shift((x, y), direction)):
			direction = utils.get_random_direction()

		move(direction)

		result = operation()
		if should_stop != None and should_stop(result):
			return

def fill_world_pumpkin():
	def fill_column_pumpkin():
		pumpkin_fills_world = False

		while not pumpkin_fills_world:
			measurements = []

			# traverse column
			for _ in range(WORLD_SIZE):
				if get_entity_type() != Entities.Pumpkin:
					crops.handle_pumpkin()

				measurement = measure()
				measurements.append(measurement)

				move(North)

			pumpkin_fills_world = len(set(measurements)) == 1
		return

	for_each_column_threaded(fill_column_pumpkin)
	
if __name__ == '__main__':
	while True:
		zig_zag_area((0, 0), (8, 3), till)