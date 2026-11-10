set_world_size(5)

import drone
import utils

PING_CROP = Entities.Bush
LISTEN_TICKS = 1000

SEND_TICKS = 200
RECEIVE_TICKS = 200

def ping():
	plant(PING_CROP)
	
# looks around the drone for evidence of a ping from a fellow drone
# returns a list of directions in which a possible ping was heard
def listen():
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
				
	return ping_directions
	
def sonar(should_stop=None, leave_asap=False, callback=None):
	# set that tracks directions of responses
	# gets reset each cycle
	pongs = None
	while should_stop == None or not should_stop(pongs):
		ping()
		pongs = listen()
		if pongs != None and len(pongs) > 0:
			if callback != None:
				callback(pongs)
			if leave_asap:
				break

	harvest()

	if pongs != None and len(pongs) > 0:
		return pongs
	return None
		
def sonar_until_response(callback=None, time_limit=None):
	def echo_heard(pong_directions=set()):
		return pong_directions != None and len(pong_directions) > 0
		
	return sonar(echo_heard, True, callback)

def sonar_for_time(seconds, callback=None):
	timer = utils.get_timer(seconds)
	# wrapper to take the args parameter, since sonar passes ping resposnes
	def timer_wrapper(args):
		return timer()

	return sonar(timer_wrapper, True, callback)

# sonars for a given time, and then returns
# if a response is heard, sonar is exited early and handshake is initiated
# returns direction if handshake completed with neighbor, None otherwise
def sonar_then_handshake():
	timer = utils.get_timer(1)
	def response_received_or_time_up(pong_directions):
		# if a response was heard
		if pong_directions != None and len(pong_directions) > 0:
			return True
		# if time is up
		if timer():
			return True

	response = sonar(response_received_or_time_up, True)

	if response != None and len(response) > 0:
		neighbor_direction = None
		# pick one neighbor in this order
		for direction in [North, East, South, West]:
			if direction in response:
				neighbor_direction = direction
				break

		if neighbor_direction != None:
			if neighbor_direction in [South, West]:
				initiate_handshake(neighbor_direction)
			else:
				wait_for_handshake(neighbor_direction)		

SYMBOLS = {
	0: Entities.Bush,
	1: Entities.Tree,
	2: Entities.Grass,
	3: Entities.Carrot,
	4: Entities.Sunflower
}
# CHARACTERS is the reverse of SYMBOLS
CHARACTERS = {}
for symbol in SYMBOLS:
	CHARACTERS[SYMBOLS[symbol]] = symbol

def wait_for_none(direction, timeout_ticks=200):
	start_tick = get_tick_count()
	neighbor_entity = get_entity_type(direction)
	while neighbor_entity != None and get_tick_count() - start_tick < timeout_ticks:
		neighbor_entity = get_entity_type(direction)

	return

def send(message):
	for character in message:
		crop = SYMBOLS[character]
		plant(crop)
		utils.wait_ticks(SEND_TICKS)
		harvest()

def receive(direction):
	signal = None
	start_tick = get_tick_count()
	while signal == None and get_tick_count() - start_tick < RECEIVE_TICKS:
		signal = get_entity_type(direction)

	if signal != None:
		return CHARACTERS[signal]

	return None

# starts the handshake process with neighbor in given direction
def initiate_handshake(direction):
	wait_for_none(direction)

	# synchronize
	syn = random() * len(SYMBOLS) // 1
	send([syn])

	# wait for acknoledgement
	ack = receive(direction)

	if ack == None or ack != (syn + 1) % len(SYMBOLS):
		print('no ack')
	else:
		print('ack')

# listens for a handshake to be initiated by neighbor in given direction
def wait_for_handshake(direction):
	wait_for_none(direction)

	syn = receive(direction)

	# acknowledge
	if syn == None:
		print('no handshake')
		return False

	ack = (syn + 1) % len(SYMBOLS)
	send([ack])


if __name__ == '__main__':
	import drone_thread
	import drone_experiments

	drone_experiments.prepare_for_party()

	set_execution_speed(1)

	drone_thread.new_thread(sonar_then_handshake, East)
	sonar_then_handshake()