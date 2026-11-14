LIST_SIZE = 1000

def get_random_list():
	l = []
	for _ in range(LIST_SIZE):
		l.append(random()*10//1)

	return l

def test():
	x = get_random_list()
	y = get_random_list()

	start_time = get_time()
	start_tick = get_tick_count()
	z = x + y
	end_time = get_time()
	end_tick = get_tick_count()

	num_ticks = end_tick - start_tick
	num_seconds = end_time - start_time

	print("using '+' to concatenate lists:", num_ticks, "ticks")
	do_a_flip()

	x = get_random_list()
	y = get_random_list()

	start_time = get_time()
	start_tick = get_tick_count()
	for item in y:
		x.append(item)
	end_time = get_time()
	end_tick = get_tick_count()

	num_ticks = end_tick - start_tick

	print("appending one list to another:", num_ticks, "ticks")
	do_a_flip()



if __name__ == '__main__':
	clear()
	test()