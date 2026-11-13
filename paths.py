import utils

WORLD_SIZE = get_world_size()

# build a path that visits every plot in the given rectangular space
# from space_zero to (space_zero[0] + width, space_zero[1] + height) inclusive
# space_zero: bottom-left of area
# returns: list of positions in the order to visit them
# 	first position will be closest to drone 
def build_space_filling_path(space_zero=(0, 0), height=WORLD_SIZE, width=WORLD_SIZE):
	vertical_zig_zags = height > width
	if vertical_zig_zags:
		zig_length = height
		num_zigs = width
	else:
		zig_length = width
		num_zigs = height 

	position = [space_zero]
	path = [[space_zero]]

	on_a_zig = [True]
	def zig():
		for _ in range(zig_length - 1):
			if vertical_zig_zags:
				position[0] = utils.shift(position[0], North)
				path[0].append(position[0])
			else:
				position[0] = utils.shift(position[0], East)
				path[0].append(position[0])
	def zag():
		for _ in range(zig_length - 1):
			if vertical_zig_zags:
				position[0] = utils.shift(position[0], South)
				path[0].append(position[0])
			else:
				position[0] = utils.shift(position[0], West)
				path[0].append(position[0])
	def zig_or_zag():
		if on_a_zig[0]:
			zig()
			on_a_zig[0] = False
		else:
			zag()
			on_a_zig[0] = True

	# ========== BUILD PATH START ==========

	for _ in range(num_zigs - 1):
		zig_or_zag()

		# go to next row/column
		if vertical_zig_zags:
			position[0] = utils.shift(position[0], East)
			path[0].append(position[0])
		else:
			position[0] = utils.shift(position[0], North)
			path[0].append(position[0])

	zig_or_zag()

	# ========== BUILD PATH END ==========

	drone_position = (get_pos_x(), get_pos_y())
	min_distance = utils.distance(path[0][0], drone_position)
	min_distance_i = 0
	for path_i in range(1, len(path[0])):
		path_position = path[0][path_i]

		distance = utils.distance(path_position, drone_position)
		if distance < min_distance:
			min_distance = distance
			min_distance_i = path_i

	rotated_path = path[0][min_distance_i:] + path[0][:min_distance_i]
	return rotated_path

if __name__ == '__main__':
	clear()
	import drone

	tiny_zig_zag = build_space_filling_path((0, 0), 1, 1)
	print('tiny area')
	for (x, y) in tiny_zig_zag:
		drone.move_to(x, y)

	tall_zig_zag = build_space_filling_path((0, 0), 32, 2)
	print('tall area')
	for (x, y) in tall_zig_zag:
		drone.move_to(x, y)

	world_zig_zag = build_space_filling_path()
	print('world area')
	for (x, y) in world_zig_zag:
		drone.move_to(x, y)


