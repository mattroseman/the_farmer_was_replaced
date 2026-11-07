import utils
import crops
import drone

WORLD_SIZE = get_world_size()

def sort_neighbors():
	measurement_survey = drone.look_around(measure, True)
	if(measurement_survey[South] != None and measurement_survey[South] > measurement_survey['current']):
		swap(South)
		
		move(South)
		sort_neighbors()
		move(North)
	
	measurement_survey = drone.look_around(measure, True)
	if(measurement_survey[West] != None and measurement_survey[West] > measurement_survey['current']):
		swap(West)
		
		move(West)
		sort_neighbors()
		move(East)

# Plant and harvest one worlds-worth of cacti	
def farm_once():
	for y in range(WORLD_SIZE):
		for x in range(WORLD_SIZE):
			crops.handle_cactus()

			sort_neighbors()
				
			if drone.is_top_right():
				# make sure the final cactus is grown
				while not can_harvest():
					do_a_flip()
				harvest()
			
			move(East)
		move(North)

# 8 min for 22 world size
def farm(should_stop=None):
	while should_stop == None or not should_stop():
		farm_once()
		
		
if __name__  == '__main__':
	clear()
	start_time = get_time()
	farm_once()
	end_time = get_time()
	while True:
		print('Cactus world farmed in', (end_time - start_time) // 60, 'minutes')
		do_a_flip()