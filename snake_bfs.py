import utils
from utils import DIRECTIONS
import drone
import breadth_first_search

WORLD_SIZE = get_world_size()

tail = [(0,0)]
apple = None

def move_step(start, end, first=False):
	if utils.distance(start, end) > 1:
		utils.error('Move step is too far away')

	drone.move_to(end[0], end[1])

	tail.append(end)
	# remove the oldest tail position, as the whole thing shifts forward
	# except on the first step, as the tail grows by one after eating the apple
	if not first:
		tail.pop(0)


# detects the next apple position, and moves the drone to there
# returns True if move was successful, False if there is no path
def go_to_apple():
	x = get_pos_x()
	y =  get_pos_y()

	target = measure()
	if target == None:
		utils.error('Not over apple, so cannot detect new position')
 
	path = breadth_first_search.search((x, y), target, tail)

	if path == None:
		return False

	for i in range(len(path)):
		step = path[i]
		move_step((x, y), step, i == 0)
		(x, y) = step

	return True

def farm(should_stop=None):
	# set the hat to start the game
	change_hat(Hats.Dinosaur_Hat)

	while should_stop == None or not should_stop():
		if not go_to_apple():
			while True:
				do_a_flip()
				# TODO check length to see if you won
				# print('You Won!')

if __name__ == '__main__':
	clear()
	farm()