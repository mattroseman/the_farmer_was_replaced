import drone
import crops
import utils

DEFAULT_SAMPLE_SIZE = 100

# run a test a sample_size number of times, and average the results from test
def benchmark(test, sample_size=DEFAULT_SAMPLE_SIZE):
	results = []
	tests_done = 0
	
	while tests_done < DEFAULT_SAMPLE_SIZE:
		if tests_done % 10 == 0 :
			print('test', tests_done)
		result = test()

		# None result means test didn't work in some way
		if result == None:
			continue
		else:
			tests_done += 1

		results.append(result)
		
	# calculate mean result
	sum = 0
	for result in results:
		sum += result
	avg = sum / len(results)
	benchmark = {
		'results': results,
		'min': min(results),
		'max': max(results),
		'avg': avg
	}
	return benchmark

# pumpkin grow test complete
# grow time min: 0.22 seconds
# grow time max: 3.72seconds
# grow avg: 1.89seconds
def test_pumpkin_grow_time():		
	harvest()
	crops.set_tilled()
	
	start_time = get_time()
	
	plant(Entities.Pumpkin)
	while get_entity_type() == Entities.Pumpkin and not can_harvest():
		pass

	end_time = get_time()

	# Dead Pumpkin means the test failed
	if get_entity_type() == Entities.Dead_Pumpkin:
		return None

	return end_time - start_time
	
# dead pumpkin grow test complete
# grow time min: 0.21 seconds
# grow time max: 3.72seconds
# grow avg:1.92seconds
def test_dead_pumpkin_grow_time():
	harvest()
	crops.set_tilled()
	
	start_time = get_time()
	
	plant(Entities.Pumpkin)
	while get_entity_type() == Entities.Pumpkin and not can_harvest():
		pass

	end_time = get_time()

	# Dead Pumpkin means the test failed
	if get_entity_type() != Entities.Dead_Pumpkin:
		return None

	return end_time - start_time
	
# fertilized pumpkin grow test
# grow time min: 0.07 seconds
# grow time max: 1.69seconds
# grow avg: 0.45seconds
def test_fertilized_pumpkin_grow_time():
	harvest()
	crops.set_tilled()
	
	start_time = get_time()
	
	plant(Entities.Pumpkin)
	use_item(Items.Fertilizer)
	use_item(Items.Fertilizer)
		
	while get_entity_type() == Entities.Pumpkin and not can_harvest():
		pass

	end_time = get_time()

	# Dead Pumpkin means the test failed
	if get_entity_type() == Entities.Dead_Pumpkin:
		return None

	return end_time - start_time

CROP_GROW_TIME_TESTS = {
	'pumpkin': test_pumpkin_grow_time,
	'fertilized pumpkin': test_fertilized_pumpkin_grow_time,
	'dead pumpkin': test_dead_pumpkin_grow_time
}


def check_crop_growtimes(crop_test=None):
	clear()
	drone.move_to(0,0)
	
	for crop_test_name in CROP_GROW_TIME_TESTS:
		if crop_test_name != crop_test:
			continue
		print(crop_test_name + ' grow test started')
		do_a_flip()
		
		crop_test = CROP_GROW_TIME_TESTS[crop_test_name]
	
		benchmark_data = benchmark(crop_test)
		
		utils.print_lines([
			str(crop_test_name) + ' grow test complete',
			'grow time min: ' + str(benchmark_data['min']) + ' seconds',
			'grow time max: ' + str(benchmark_data['max']) + 'seconds',
			'grow avg:' + str(benchmark_data['avg']) + ' seconds',
		])
	
	
if __name__ == '__main__':
	check_crop_growtimes('fertilized pumpkin')