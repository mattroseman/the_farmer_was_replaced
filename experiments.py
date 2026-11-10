import utils

def test_tick_count():
	start_tick = get_tick_count()
	utils.wait_ticks(200)
	end_tick = get_tick_count()
	
	print(end_tick - start_tick)

def get_unlocked_hats():
	unlocked_hats = set()

	for hat in Hats:
		if num_unlocked(hat) > 0:
			unlocked_hats.add(hat)

	for hat in unlocked_hats:
		change_hat(hat)
		print(hat)
		do_a_flip()


if __name__ == '__main__':
	# test_tick_count()
	get_unlocked_hats()