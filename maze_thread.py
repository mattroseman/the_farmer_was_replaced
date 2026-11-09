import utils
import drone


# moves the drone down a crossroads, and starts a find-treasure thread on this branch
def explore_branch(direction, position, path, visited):
	move(direction)
	return find_treasure_thread(position, path, visited)

def find_treasure_thread(position, path=[], visited=set()):
	starting_position = position

	child_threads = set()
	# track if there were any branches on the path, since this thread has started
	# to know if you should backtrack
	branching_paths_left = False

	while get_entity_type() == Entities.Hedge:
		visited.add(position)

		# check if any child drones finished, and collect their visited sets
		pruned_threads = set()
		for thread in child_threads:
			if has_finished(thread):
				thread_visited = wait_for(thread)
				for thread_visit in thread_visited:
					visited.add(thread_visit)

				pruned_threads.add(thread)
		for thread in pruned_threads:
			child_threads.remove(thread)

		steps_to_take = []
		for direction in utils.get_randomized_directions():
			new_position = utils.shift(position, direction)
			if new_position not in visited and can_move(direction):
				steps_to_take.append(direction)
				visited.add(new_position)

		# dead end
		if len(steps_to_take) == 0:
			# if there aren't any branching paths to take
			if not branching_paths_left:
				return visited

			back = utils.OPPOSITE_DIRECTION[path.pop()]
			move(back)
			position = utils.shift(position, back)

			continue

		# spawn drones for all but the first move
		for step in steps_to_take[1:]:
			new_position = utils.shift(position, step)
			if num_drones() < max_drones():
				new_path = utils.copy_list(path)
				new_path.append(step)
				thread = spawn_drone(explore_branch, step, new_position, new_path, visited)
				child_threads.add(thread)

		move(steps_to_take[0])
		position = utils.shift(position, steps_to_take[0])
		path.append(steps_to_take[0])

	if get_entity_type() == Entities.Treasure:
		treasure_found()

def treasure_found():
	harvest()
	print('Maze completed')
	do_a_flip()
	maze()

def maze():
	clear()
	drone.move_to(0, 0)
	(x, y) = (0, 0)

	plant(Entities.Bush)
	num_weird_substance = get_world_size() * 2**(num_unlocked(Unlocks.Mazes) - 1)
	use_item(Items.Weird_Substance, num_weird_substance)

	find_treasure_thread((x, y))


if __name__ == '__main__':
	# set_world_size(10)
	# set_execution_speed(1)
	maze()