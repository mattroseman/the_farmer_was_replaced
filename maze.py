import drone
import utils


def on_treasure():
	return get_entity_type() == Entities.Treasure

# recursive version of DFS algorithm used in find_treasure
# def find_treasure__dfs_recursive(position):
# 	if get_entity_type() == Entities.Treasure:
# 		harvest()
# 		return True
# 		
# 	visited.add(position)
# 		
# 	for direction in utils.DIRECTIONS:
# 		new_position = utils.shift(position, direction)
# 		if new_position not in visited and can_move(direction):
# 			move(direction)
# 			treasure_found = find_treasure(utils.shift(position, direction))
# 			if treasure_found:
# 				return True
# 			else:
# 				move(utils.OPPOSITE_DIRECTION[direction])
# 	
# 	return False

def find_treasure(position):
	path = []
	visited = set()

	while not on_treasure():
		visited.add(position)

		moved = False
		for direction in utils.DIRECTIONS:
			new_position = utils.shift(position, direction)
			if new_position not in visited and can_move(direction):
				move(direction)
				position = new_position

				path.append(direction)
				moved = True
				break

		# dead end: undo the last step, like returning False from the recursion
		if not moved:
			if len(path) == 0:
				return False
			back = utils.OPPOSITE_DIRECTION[path.pop()]
			move(back)
			position = utils.shift(position, back)

	harvest()
	return True
			

def maze():
	while True:
		drone.move_to(0, 0)
		(x, y) = (0, 0)
		
		plant(Entities.Bush)
		num_weird_substance = get_world_size() * 2**(num_unlocked(Unlocks.Mazes) - 1)
		use_item(Items.Weird_Substance, num_weird_substance)

		success = find_treasure((x, y))
		if not success:
			utils.error('Maze solve failed')


if __name__ == '__main__':
	clear()
	
	maze()