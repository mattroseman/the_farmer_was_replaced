import utils

def test_tick_count():
	start_tick = get_tick_count()
	utils.wait_ticks(200)
	end_tick = get_tick_count()
	
	print(end_tick - start_tick)
	
if __name__ == '__main__':
	test_tick_count()