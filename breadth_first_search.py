import utils
from utils import DIRECTIONS

WORLD_SIZE = get_world_size()


def position_possible(position, visited, tail):
	# skip if the position was already visited
	if position in visited:
		return False

	# check if next position is out of bounds
	if not utils.inbounds(position):
		return False

	# check if the tail is in the way
	if position in tail:
		return False
		
	return True

# shift tail by adding on a new step, and shifting forward by taking off the last
# returns the new tail without modifying the given one
def shift_tail(tail, new_step):
	return [new_step] + tail[:-1]

def search(start, end, tail):
	# queue of positions along paths to explore
	# {
	# 	"position": (x, y),
	# 	"tail": [(x1, y1), (x2, y2), ...]
	# 	"path": [(x1, y1), (x2, y2), ...]
	# }
	to_visit = [start] 
	states = {
		start: {
			'tail': tail,
			'path': [start]
		}
	}
	visited = set()

	first_step = True

	while len(to_visit) > 0:
		position = to_visit.pop(0)
		state = states[position]
		tail = state['tail']
		path = state['path']

		quick_print('visiting', position)

		visited.add(position)
	
		# look around for the end, and add possible next steps to to_visit queue
		for direction in DIRECTIONS:
			neighbor = utils.shift(position, direction)
			
			if neighbor == end:
				return path + [end]
				
			if not position_possible(neighbor, visited, tail):
				continue
			
			# if this position hasn't already been checked, add to to_visit queue
			if neighbor not in to_visit and neighbor not in visited:
				# update tail
				if not first_step:
					new_tail = [neighbor] + tail[:-1]  # shift the tail forward
				else:
					# add next position to head of tail,
					# as it grows the first step
					new_tail = [neighbor] + tail
					first_step = False 

				to_visit.append(neighbor)
				states[neighbor] = {
					"tail": new_tail,
					"path": path + [neighbor]
				}

	# if the end wasn't found, return None as it's unreacheable
	return None

if __name__ == '__main__':
	path = search((0, 0), (5, 7), (0, 0))
	
	print(path)