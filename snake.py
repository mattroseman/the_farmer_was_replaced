import drone
import utils

tail_length = 0
tail = []

# TODO
# keep farm matrix, tracking tail & apple
farm_state = utils.get_farm_state_matrix()
# values are you, tail, or apple
# Then write pathfining algorithm to get from you to apple, with tail being walls you can't cross
# bfs or djikstra or something

def try_move(direction):
	if move(direction):
		return True
	else:
		utils.error("Could not move "  + str(direction))

def snake_move_to(x, y):
	current_x = get_pos_x()
	current_y = get_pos_y()
	target_x = x
	target_y = y
	has_grown = False
	
	while current_x != target_x:
		if current_x < target_x:
			try_move(East)
			current_x += 1
			tail.append((current_x, current_y))
			if has_grown:
				tail.pop(0)
			has_grown = True
		if current_x > target_x:
			try_move(West)
			current_x -= 1
			tail.append((current_x, current_y))
			if has_grown:
				tail.pop(0)
			has_grown = True
			
	while current_y != target_y:
		if current_y < target_y:
			try_move(North)
			current_y += 1
			tail.append((current_x, current_y))
			if has_grown:
				tail.pop(0)
			has_grown = True
		else:
			try_move(South)
			current_y -= 1
			tail.append((current_x, current_y))
			if has_grown:
				tail.pop(0)
			has_grown = True

def farm(should_stop=None):
	change_hat(Hats.Dinosaur_Hat)
	while should_stop == None or not should_stop():
		next_pos = measure()
		print(next_pos)
		snake_move_to(next_pos[0], next_pos[1])
		print(tail)
		do_a_flip()

if __name__ == '__main__':
	clear()
	farm()