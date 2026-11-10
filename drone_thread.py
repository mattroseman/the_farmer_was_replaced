import drone

def build_shift_and_doer(direction, operation, args=()):
	def shift_then_do():
		move(direction)
		if args == () or args == None:
			operation()
		else:
			operation(args)

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
	if direction == None:
		# if no args to include
		if args == () or args == None:
			spawn_drone(operation)
		else:
			spawn_drone(operation, args)
	else:
		shift_then_do_operation = build_shift_and_doer(direction, operation, args)
		
		spawn_drone(shift_then_do_operation)