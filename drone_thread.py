import drone

WORLD_SIZE = get_world_size()

def build_shift_and_doer(direction, operation, args=()):
	def shift_then_do():
		move(direction)
		if args == () or args == None:
			return operation()
		else:
			return operation(args)

	return shift_then_do

def build_move_to_and_doer(destination, operation, args=(), no_wrap=False):
	def move_to_then_do():
		if no_wrap:
			drone.move_to_no_warp(destination[0], destination[1])
		else:
			drone.move_to(destination[0], destination[1])
		if args == () or args == None:
			operation()
		else:
			operation(args)

	return move_to_then_do
	
# new_thread() spawns a drone to perform the given operation
# optionally specify direction to spawn a drone one-off from current position
# optionally pass an argument tuple, if operation accepts a single-tuple argument
def new_thread(operation, direction=None, args=()):
	thread = None

	if direction == None:
		# if no args to include
		if args == () or args == None:
			thread = spawn_drone(operation)
		else:
			thread = spawn_drone(operation, args)
	else:
		shift_then_do_operation = build_shift_and_doer(direction, operation, args)
		
		thread = spawn_drone(shift_then_do_operation)

	return thread

# waits for children threads to complete, then returns a list of their results
def wait_for_children(children):
	results = []
	for thread in children:
		result = wait_for(thread)
		results.append(result)
		
	return results


if __name__ == '__main__':
	clear()
	import crops
	import routines

	routines.till_world()