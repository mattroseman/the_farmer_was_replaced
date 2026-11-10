set_world_size(5)
# set_execution_speed(1)

import drone
import utils
import drone_thread
import crops
import routines

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

	should_stop_state = [False]
	def handshake_completed(direction):
		should_stop_state[0] = True

	def should_stop():
		return should_stop_state[0]

	drone.perambulate_no_wrap(drone_talk.sonar_then_handshake, None, True)

def prepare_for_party():
	def prepare_plot_for_party():
		harvest()
		crops.set_tilled()

	routines.for_each_plot_threaded(prepare_plot_for_party)
	

def party(num_attending=max_drones()):
	prepare_for_party()

	for _ in range(num_attending):
		spawn_point = utils.get_random_plot()
		go_to_spawn_and_mingle = drone_thread.build_move_to_and_doer(spawn_point, perambulate_and_greet, None, True)
		drone_thread.new_thread(go_to_spawn_and_mingle)
	
if __name__ == '__main__':
	party(2)

# IDEAS:
	# have drones constantly looking around, and quickly planting something and harvesting it
	# this can be how they get each other's attention
	# then you can have them communicate in morse code, and exchange information