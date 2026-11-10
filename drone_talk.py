import drone
import utils

PING_CROP = Entities.Bush
LISTEN_TICKS = 4000
PING_TICKS = 400

def ping():
	plant(PING_CROP)
	utils.wait_ticks(PING_TICKS)
	harvest()
	
# looks around the drone for evidence of a ping from a fellow drone
# returns a list of directions in which a possible ping was heard
# leave_asap means function returns as soon as any response is heard
def listen(leave_asap=False):
	ping_directions = set()
	
	# randomly slightly offset the number of ticks listening,
	# to avoid syncing with other drones' sonar
	# +/-15% of LISTEN_TICKS
	nonce = random()
	offset = nonce * (LISTEN_TICKS * 0.15 // 1)
	if utils.coinflip():
		offset = -1 * offset
	
	start_tick = get_tick_count()
	while get_tick_count() - start_tick < (LISTEN_TICKS + offset):
		echo = drone.look_around(get_entity_type)
		for direction in utils.DIRECTIONS:
			if echo[direction] == PING_CROP:
				ping_directions.add(direction)
				
		if leave_asap:
			return ping_directions

	return ping_directions
	
def sonar(should_stop=None, leave_asap=False):
	# set that tracks directions of responses
	# gets reset each cycle
	pongs = None
	while should_stop == None or not should_stop(pongs):
		ping()
		pongs = listen(leave_asap)
		
def sonar_until_response():
	def echo_heard(pong_directions=set()):
		return pong_directions != None and len(pong_directions) > 0
		
	sonar(echo_heard, True)
	

if __name__ == '__main__':
	while True:
		sonar_until_response()
		do_a_flip()