import drone
import utils
import threading

import drone_talk

def can_you_sense_other_drones():
	drone.move_to(0, 0)
	
	threading.new_thread(drone.wait_around, East)
	
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
	friend = threading.new_thread(sonar_and_celebrate, East)

	while True:
		drone_talk.sonar_until_response()
		do_a_flip()

def perambulate_and_greet():
	clear()
	
if __name__ == '__main__':
	conversation()

# IDEAS:
	# have drones constantly looking around, and quickly planting something and harvesting it
	# this can be how they get each other's attention
	# then you can have them communicate in morse code, and exchange information