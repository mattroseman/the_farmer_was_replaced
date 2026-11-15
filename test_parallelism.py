# alone took 0.67 seconds, 4048 ticks
# w/a friend took 0.7 seconds, 4248 ticks
# w/a group took 1 seconds 6072 ticks

set_world_size(5)

import utils
import drone
import quicksort

def wait_alone():
	checkpoint = utils.set_checkpoint()

	utils.wait_ticks(4000)

	(seconds, ticks, _) = checkpoint()['since_checkpoint']
	print('alone took', seconds, 'seconds,', ticks, 'ticks')

def wait_with_a_friend():
	checkpoint = utils.set_checkpoint()

	child = spawn_drone(utils.wait_ticks, 4000)
	utils.wait_ticks(4000)
	wait_for(child)

	(seconds, ticks, _) = checkpoint()['since_checkpoint']
	print('w/a friend took', seconds, 'seconds,', ticks, 'ticks')

def wait_with_a_group():
	checkpoint = utils.set_checkpoint()

	children = set()
	for _ in range (10):
		child = spawn_drone(utils.wait_ticks, 4000)
		children.add(child)

	utils.wait_ticks(4000)

	for child in children:
		wait_for(child)

	(seconds, ticks, _) = checkpoint()['since_checkpoint']
	print('w/a group took', seconds, 'seconds', ticks, 'ticks')

def sort_list_alone():
	l = []
	for _ in range(1000):
		l.append(random()*100//1)

	# quick_print(l)
	
	checkpoint = utils.set_checkpoint()
	sorted = quicksort.sort(l, utils.is_greater_than, 0)
	(seconds, ticks, _) = checkpoint()['since_checkpoint']

	# quick_print(sorted)

	print('sorting alone took', seconds, 'seconds', ticks, 'ticks')

def sort_with_friends():
	l = []
	for _ in range(1000):
		l.append(random()*100//1)

	# quick_print(l)
	
	checkpoint = utils.set_checkpoint()
	sorted = quicksort.sort(l, utils.is_greater_than, max_drones() - 1)
	(seconds, ticks, _) = checkpoint()['since_checkpoint']

	# quick_print(sorted)

	print('sorting with friends', seconds, 'seconds', ticks, 'ticks')



if __name__ == '__main__':
	clear()

	# wait_alone()
	# wait_with_a_friend()
	# wait_with_a_group()

	# sorting alone took 11.53 seconds 70055 ticks
	sort_list_alone()
	# sorting with friends 5.32 seconds 32291 ticks
	sort_with_friends()

	drone.wait_around()
