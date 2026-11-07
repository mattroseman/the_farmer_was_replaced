import drone
import bubble_sort
from cactus_farm import plant_world

WORLD_SIZE = get_world_size()

def farm_run():
	plant_world()
	bubble_sort.sort()
	
	drone.move_to(WORLD_SIZE-1, WORLD_SIZE-1)
	harvest()

# 13 min
def farm(should_stop=None):
	while should_stop == None or not should_stop():
		farm_run()

if __name__ == '__main__':
	clear()
	
	start_time = get_time()
	farm_run()
	run_time = get_time() - start_time
	
	drone.move_to(0, 0)
	while True:
		print('Cactus world farmed in', run_time // 60, 'minutes')
		do_a_flip()