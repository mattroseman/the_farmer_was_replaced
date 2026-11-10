import utils
from utils import DIRECTIONS

# TODO attempt to always pick the direction toward the end

# searches for a path from start to end, avoiding a tail
# returns an array of positions, from start to end, that avoids the
# returns None if there is no path
def search(start, end, tail, first_step, visited=[]):
	for direction in DIRECTIONS:
		next_position = utils.shift(start, direction)
		
		# check if the next position was already visited
		if next_position in visited:
			continue
		visited.append(next_position)

		if not utils.inbounds(next_position):
			continue

		# if the tail's in the way, this direction is a dead end
		if next_position in tail:
			continue
			
		# update tail
		if not first_step:
			new_tail = [next_position] + tail[:-1]  # shift the tail forward
		else:
			# add next position to head of tail,
			# as it grows the first step
			new_tail = [next_position] + tail
			first_step = False 

		if next_position == end:
			return [start, end]

		path = search(next_position, end, new_tail, first_step, visited)
		if path != None:
			path.insert(0, start)
			return path

	# if none of the directions worked, return None
	return None
	