import utils
import crops

WORLD_SIZE = get_world_size()

def move_to_no_warp(x, y):
	target_x = x
	target_y = y
	current_x = get_pos_x()
	current_y = get_pos_y()
	
	if target_x >= WORLD_SIZE:
		utils.error('ERROR: move_to x is outside of world')
	if target_y >= WORLD_SIZE:
		utils.error('ERROR: move_to y is outside of world')
		
	while (current_x, current_y) != (target_x, target_y):
		if target_x != current_x:
			if target_x < current_x:
				move(West)
				current_x -= 1
			else:
				move(East)
				current_x += 1
		if target_y != current_y:
			if target_y < current_y:
				move(South)
				current_y -= 1
			else:
				move(North)
				current_y += 1
	
def move_to(x, y):
	target_x = x
	target_y = y
	current_x = get_pos_x()
	current_y = get_pos_y()
	
	if target_x >= WORLD_SIZE:
		utils.error('ERROR: move_to x is outside of world')
	if target_y >= WORLD_SIZE:
		utils.error('ERROR: move_to y is outside of world')
	
	while (current_x, current_y) != (target_x, target_y):
		if target_x != current_x:
			if (target_x - current_x) % WORLD_SIZE < (current_x - target_x) % WORLD_SIZE:
				move(East)
			else:
				move(West)
			
			current_x = get_pos_x()
		
		if target_y != current_y:
			if (target_y - current_y) % WORLD_SIZE < (current_y - target_y) % WORLD_SIZE:
				move(North)
			else:
				move(South)
				
			current_y = get_pos_y()
			
def look_around(sense, no_wrap=False):
	# if no_wrap specified, don't look past the world edges, to the other side
	if no_wrap:
		x = get_pos_x()
		y = get_pos_y()
		
		survey = {
			'current': sense(),
			North: None,
			East: None,
			South: None,
			West: None
		}
		if y < WORLD_SIZE - 1:
			survey[North] = sense(North)
		if x < WORLD_SIZE - 1:
			survey[East] = sense(East)
		if y > 0:
			survey[South] = sense(South)
		if x > 0:
			survey[West] = sense(West)
			
		return survey
		
	return {
		'current': sense(),
		North: sense(North),
		East: sense(East),
		South: sense(South),
		West: sense(West)
	}
	
def is_top_right():
	x = get_pos_x()
	y = get_pos_y()
	world_size = get_world_size()
	
	return x == world_size - 1 and y == world_size - 1
				
if __name__ == '__main__':
	move_to(1,1)
	do_a_flip()
	move_to(4,5)
	do_a_flip()
	move_to(3,3)
			