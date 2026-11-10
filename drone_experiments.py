set_world_size(20)
# set_execution_speed(1)

import drone
import utils
import drone_thread

import drone_talk

def can_you_sense_other_drones():
	drone.move_to(0, 0)
	
	drone_thread.new_thread(drone.wait_around, East)
	
	results = {
		'measure()': measure(East),
		'get_entity_type()': get_entity_type(East),
	}
	
	result_lines = []
	for measurement in results:
		result_lines.append(str(measurement) + ': ' + str(results[measurement]))
		
	utils.print_lines(result_lines)
	
def conversation():
	clear()

	def sonar_and_celebrate():
		while True:
			drone_talk.sonar()
			do_a_flip()
	friend = drone_thread.new_thread(sonar_and_celebrate, East)

	while True:
		drone_talk.sonar_until_response()
		do_a_flip()

def perambulate_and_greet():
	# dawn a party hat
	drone.wear_random_hat()

	def sonar_then_greet():
		def greet(prongs):
			do_a_flip()
		response = drone_talk.sonar_for_time(1, greet)

	drone.perambulate_no_wrap(sonar_then_greet)

def party(num_attending=max_drones()):
	for _ in range(num_attending):
		spawn_point = utils.get_random_plot()
		go_to_spawn_and_mingle = drone_thread.build_move_to_and_doer(spawn_point, perambulate_and_greet, None, True)
		drone_thread.new_thread(go_to_spawn_and_mingle)
	
if __name__ == '__main__':
	party(8)

# IDEAS:
	# have drones constantly looking around, and quickly planting something and harvesting it
	# this can be how they get each other's attention
	# then you can have them communicate in morse code, and exchange information