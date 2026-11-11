import drone
import utils

LISTEN_TICKS = 1000
# when a drone detects another drone, it may wait a grace period of ticks to give the other drone a chance to see it
GRACE_TICKS = 250

HANDSHAKE_TICKS_WAIT = 450

# ping crop and directional crops are for drones to recognize each other and orient each other
PING_CROP = Entities.Bush
GENERIC_PONG = 'generic'
DIRECTIONAL_CROP = {
	North: Entities.Tree,
	East: Entities.Grass,
	South: Entities.Carrot,
	West: Entities.Sunflower
}
DIRECTED_PONG = 'directed'
# symbols and digits are for communicating after a handshake is established
SYMBOLS = {
	0: Entities.Bush,
	1: Entities.Tree,
	2: Entities.Grass,
	3: Entities.Carrot,
	4: Entities.Sunflower
}
DIGITS = utils.reverse_map(SYMBOLS) 

FOLLOWING = 'following'
LEADING = 'leading'

# encode a digit 0-4 into the corresponding symbol (crop)
def encode(digit):
	if digit not in SYMBOLS:
		utils.error('digit ' + str(digit) + ' has no corresponding symbol')
	return SYMBOLS[digit]

# decode a crop (symbol) into the corresponding digit
def decode(symbol):
	# unknown symbols are expected, and should be ignored
	if symbol not in DIGITS:
		return None
	return DIGITS[symbol]

def ping(direction=None):
	# plant directional ping
	if direction:
		plant(DIRECTIONAL_CROP[direction])
	# plant generic ping
	else:
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
def listen() -> dict:
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
				pongs[direction] = GENERIC_PONG
			elif pong == DIRECTIONAL_CROP[utils.OPPOSITE_DIRECTION[direction]]:
				pongs[direction] = DIRECTED_PONG
			# if the direction shows a directional crop in the wrong way, reset pong state
			elif pong != None:
				pongs[direction] = None

		# decide to leave
		for direction in pongs:
			# if a directed pong was heard, leave early
			if pongs[direction] == 'directed':
				return pongs

			# if a generic pong was heard, wait a grace period, then leave early
			if pongs[direction] == 'generic':
				# move up the end tick to end early
				end_tick = min(get_tick_count() + GRACE_TICKS, end_tick)
				
	return pongs
	
# pings surrounding drones by planting a crop, and listens for the pings of other drones
def sonar(should_stop: function=None) -> set:
	pongs = None
	harvest()

	while should_stop == None or not should_stop(pongs):
		ping()
		pongs = listen()
		for pong_direction in pongs:
			if pongs[pong_direction] != None:
				break

	# clean up any ping crops
	harvest()

	return pongs

# attempts to handshake with drone in given direction
# returns the drone's state in relationship (FOLLOWING or LEADING), if handshake succeeds
# returns None if handshake fails
def handshake(direction: Direction) -> str:
	# PHASE 1: DIRECTIONAL PING
	# phase 1 involves changing the ping crop to one specifying the direction of the ping
	# so if you have a neighbor to the North (handshake(North)) you plant a DIRECTIONAL_CROP[North]

	# SYN stands for synchronization, as in SYN, SYN-ACK, ACK protocol
	syn = DIRECTIONAL_CROP[direction]
	expected_ack = DIRECTIONAL_CROP[utils.OPPOSITE_DIRECTION[direction]]

	ping(direction)

	ack_received = drone.wait_for_crop(expected_ack, direction, HANDSHAKE_TICKS_WAIT)
	# wait a little for your neighbor to see your directional syn crop
	utils.wait_ticks(GRACE_TICKS)

	if not ack_received:
		harvest()
		return False

	# PHASE 2: CHALLENGE SYN/ACK
	# Your neighbor has a directional crop pointing to you and you have one pointing to them
	# now confirm it's a drone, and not happenstance, by changing the SYN and ACK

	# The North or East neighbor sends a random SYN (different from PHASE 1 crops),
	# and the South or West neighbor responds with SYN + 1 as the ACK
	# This establishes the north/east drone as the leader, and the south/west drone as the follower
	if direction == South or direction == West:
		# choose new SYN crop, different from the first directional ping crop,
		# or whose expected ACK is what your neighbor already has
		syn2 = None
		while syn2 == None or syn2 == syn or (DIGITS[syn2] + 1) % len(SYMBOLS) == DIGITS[expected_ack]:
			syn2 = encode(random() * len(SYMBOLS) // 1)
		expected_ack2 = encode((decode(syn2) + 1) % len(SYMBOLS))

		harvest()
		plant(syn2)

		ack2_received = drone.wait_for_crop(expected_ack2, direction, HANDSHAKE_TICKS_WAIT)
		if ack2_received:
			harvest()
			return LEADING
	# otherwise wait for your neighbor's SYN
	else:
		received_syn = drone.wait_for_crop_except([expected_ack], direction, HANDSHAKE_TICKS_WAIT)
		if received_syn == None:
			harvest()
			return False

		ack = encode((decode(received_syn) + 1) % len(SYMBOLS))

		harvest()

		plant(ack)
		utils.wait_ticks(HANDSHAKE_TICKS_WAIT)
		harvest()

		return FOLLOWING

	harvest()
	return False

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

# sonars for a given time, or until a response is heard, then attempts handshake
# returns (direction of handshake, state of this drone in relations), or None if sonar times out or handshake fails
def sonar_then_handshake() -> tuple[Direction, str] | None:
	timer = utils.get_timer(1)
	# to replant when you're done
	initial_crop = get_entity_type()

	# should-stop function for sonar
	def response_received_or_time_up(pongs):
		# if a response was heard
		if pongs != None and len(pongs) > 0:
			return True
		# if time is up
		if timer():
			return True

	response = sonar(response_received_or_time_up)

	neighbor_direction = None
	for direction in response:
		# any directed pongs take precedence
		if response[direction] == 'directed':
			neighbor_direction = direction
			break

		if response[direction] == 'generic':
			neighbor_direction = direction


	if neighbor_direction != None:
		handshake_result = handshake(neighbor_direction)
		if initial_crop != None:
			plant(initial_crop)
		return handshake_result

	if initial_crop != None:
		plant(initial_crop)
	return None


if __name__ == '__main__':
	import drone_thread
	import crops
	import routines

	routines.for_each_plot_threaded(crops.set_tilled)

	# set_execution_speed(1)

	drone_thread.new_thread(sonar_then_handshake, East)
	sonar_then_handshake()