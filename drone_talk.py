set_world_size(5)

import drone
import utils

# when a drone is pinging, use ping crop
PING_CROP = Entities.Bush
# when a drone has detected a neighbor, use directional crop to synchronize with neighbor
DIRECTIONAL_CROP = {
	North: Entities.Tree,
	East: Entities.Grass,
	South: Entities.Carrot,
	West: Entities.Sunflower
}
LISTEN_TICKS = 1000
# when a drone detects another drone, it may wait a grace period of ticks to give the other drone a chance to see it
GRACE_TICKS = 250

HANDSHAKE_TICKS_WAIT = 450

def ping():
	plant(PING_CROP)
	
# looks around the drone for evidence of a ping from a fellow drone
# returns a dict of each direction and a string if a pong was heard
# None means no pong heard, 'directed' means a directed pong (orientated to you) was heard,
# and 'generic' means a non-directed pong was heard
# Example: {
# 	North: None,
# 	East: 'directed',
# 	South: None,
#	West: 'generic'
# }
def listen():
	# None means no pong heard, 'directed' means directed pong heard, and 'generic' means generic pong heard
	pongs = {
		North: None,
		East: None,
		South: None,
		West: None
	}
	
	# randomly slightly offset the number of ticks listening,
	# to avoid syncing with other drones' sonar
	# +/-15% of LISTEN_TICKS
	nonce = random()
	offset = nonce * (LISTEN_TICKS * 0.15 // 1)
	if utils.coinflip():
		offset = -1 * offset
	
	start_tick = get_tick_count()
	end_tick = start_tick + LISTEN_TICKS + offset
	while get_tick_count() < end_tick: 
		echo = drone.look_around(get_entity_type)
		for direction in utils.DIRECTIONS:
			pong = echo[direction]
			if pong == PING_CROP:
				pongs[direction] = 'generic'
			elif pong == DIRECTIONAL_CROP[utils.OPPOSITE_DIRECTION[direction]]:
				pongs[direction] = 'directed'
			# if the direction shows a directional crop in the wrong way, reset pong state
			elif pong != None:
				pongs[direction] = None

		# if a directed pong was heard leave early
		for direction in pongs:
			if pongs[direction] == 'directed':
				return pongs

			# if a generic pong was heard, wait a grace period, then leave early
			if pongs[direction] == 'generic':
				# move up the end tick to end early
				end_tick = min(get_tick_count() + GRACE_TICKS, end_tick)
				
	return pongs
	
def sonar(should_stop=None, leave_asap=False):
	# set that tracks directions of responses
	# gets reset each cycle
	pongs = None
	while should_stop == None or not should_stop(pongs):
		ping()
		pongs = listen()
		if pongs != None and len(pongs) > 0:
			if leave_asap:
				break

	harvest()

	return pongs
		
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
	def response_received_or_time_up(pongs):
		# if a response was heard
		if pongs != None and len(pongs) > 0:
			return True
		# if time is up
		if timer():
			return True

	response = sonar(response_received_or_time_up, True)
	neighbor_direction = None
	for direction in response:
		# any directed pongs take precedence
		if response[direction] == 'directed':
			neighbor_direction = direction
			break

		if response[direction] == 'generic':
			neighbor_direction = direction


	if neighbor_direction != None:
		handshake(neighbor_direction)

	drone.wait_around()

def handshake(direction):
	# the syn that was already planted (used later to avoid sending the same one again)
	syn = DIRECTIONAL_CROP[direction]
	expected_ack = DIRECTIONAL_CROP[utils.OPPOSITE_DIRECTION[direction]]

	plant(DIRECTIONAL_CROP[direction])

	ack_received = drone.wait_for_crop(expected_ack, direction, HANDSHAKE_TICKS_WAIT)
	# TODO look into waiting here to let other drone see your first SYN crop

	if ack_received:
		# print('ack recieved')
		# if you've received an ACK and you're neighbor is South/West of you, send a SYN message
		if direction == South or direction == West:
			syn2 = None
			# make sure the second sync isn't the crop used for the first, or have an expected response
			# equal to the ACK the other drone just sent (ensuring for a proper ACK a new crop must be planted)
			while syn2 == None or syn2 == syn or (DIGITS[syn2] + 1) % len(SYMBOLS) == DIGITS[expected_ack]:
				syn2 = encode(random() * len(SYMBOLS) // 1)
			harvest()
			plant(syn2)
			expected_ack2 = encode((decode(syn2) + 1) % len(SYMBOLS))

			ack2_received = drone.wait_for_crop(expected_ack2, direction, HANDSHAKE_TICKS_WAIT)
			if ack2_received:
				print("Handshake success, I'm leading")
				return True
		# otherwise wait for your neighbors SYN
		else:
			received_syn = drone.wait_for_crop_except([expected_ack], direction, HANDSHAKE_TICKS_WAIT)
			if received_syn == None:
				return False

			ack = encode((decode(received_syn) + 1) % len(SYMBOLS))

			harvest()
			plant(ack)
			print("Handshake success, I'm following")
			return True

	return False

SYMBOLS = {
	0: Entities.Bush,
	1: Entities.Tree,
	2: Entities.Grass,
	3: Entities.Carrot,
	4: Entities.Sunflower
}
DIGITS = utils.reverse_map(SYMBOLS) 

def encode(digit):
	if digit not in SYMBOLS:
		utils.error('digit ' + str(digit) + ' has no corresponding symbol')
	return SYMBOLS[digit]

def decode(symbol):
	# unknown symbols are expected, and should be ignored
	if symbol not in DIGITS:
		return None
	return DIGITS[symbol]

# def send(message):
# 	# send message digit at a time
# 	for digit in message:
# 		symbol = encode(digit)
# 		# symbol visible for ~200 ticks
# 		success = plant(symbol)
# 		if not success:
# 			utils.error("couldn't plant " + str(symbol))
# 		harvest()
# 
# def receive(direction):
# 	received_symbol = None
# 	start_tick = get_tick_count()
# 	while received_symbol == None and get_tick_count() - start_tick < RECEIVE_TICKS:
# 		received_symbol = get_entity_type(direction)
# 
# 	if received_symbol != None:
# 		return decode(received_symbol)
# 
# 	return None


if __name__ == '__main__':
	import drone_thread
	import crops
	import routines

	routines.for_each_plot_threaded(crops.set_tilled)

	# set_execution_speed(1)

	drone_thread.new_thread(sonar_then_handshake, East)
	sonar_then_handshake()