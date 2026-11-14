# lists
# z = x + y | 2000 ticks
# for item in y: x.append(item) | 1001 ticks
# x += y | 1000 ticks
# x = x + y | 2000 ticks

# sets
# for item in y: x.add(item) | 964 ticks
# looping sets and combining into a third | 1919 ticks

LIST_SIZE = 1000
SET_SIZE = 1000
SET_RANGE = SET_SIZE * 10

def get_random_list():
	l = []
	for _ in range(LIST_SIZE):
		l.append(random()*10//1)

	return l

def get_random_set():
	s = set()
	for _ in range(SET_SIZE):
		s.add(random()*SET_RANGE//1)

	return s

def test_list_concat():
	print('TESTING LISTS:')

	x = get_random_list()
	y = get_random_list()

	start_time = get_time()
	start_tick = get_tick_count()
	z = x + y
	end_time = get_time()
	end_tick = get_tick_count()

	num_ticks = end_tick - start_tick
	num_seconds = end_time - start_time

	print("z = x + y |", num_ticks, "ticks")
	do_a_flip()

	x = get_random_list()
	y = get_random_list()

	start_tick = get_tick_count()
	for item in y:
		x.append(item)
	end_tick = get_tick_count()
	num_ticks = end_tick - start_tick

	print("for item in y: x.append(item) |", num_ticks, "ticks")
	do_a_flip()

	x = get_random_list()
	y = get_random_list()

	start_tick = get_tick_count()
	x += y
	end_tick = get_tick_count()
	num_ticks = end_tick - start_tick

	print("x += y |", num_ticks, "ticks")
	do_a_flip()

	x = get_random_list()
	y = get_random_list()

	start_tick = get_tick_count()
	x = x + y
	end_tick = get_tick_count()
	num_ticks = end_tick - start_tick

	print("x = x + y |", num_ticks, "ticks")
	do_a_flip()

def test_set_union():
	print('TESTING SETS:')

	x = get_random_set()
	y = get_random_set()

	start_tick = get_tick_count()
	for item in y:
		x.add(item)
	end_tick = get_tick_count()
	num_ticks = end_tick - start_tick

	print("for item in y: x.add(item) |", num_ticks, "ticks")

	x = get_random_set()
	y = get_random_set()
	z = set()

	start_tick = get_tick_count()
	for item in x:
		z.add(item)
	for item in y:
		z.add(item)
	end_tick = get_tick_count()
	num_ticks = end_tick - start_tick

	print("looping sets and combining into a third |", num_ticks, "ticks")

if __name__ == '__main__':
	clear()
	test_list_concat()
	test_set_union()