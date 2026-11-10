import utils
import drone_thread

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

# test how plant and harvest changes a plot's entity type, over tick time
# plant started 12593.98
# plant detected 12593.99
# plant done 12594.48
# plant detected after 414 ticks
# plant no longer detected after 613 ticks
# plant detectable for 199 ticks
# results indicate the plant is visible instantly (or in ~1 tick)
# and harvest removes the plant instantly (or in ~1 tick)
def test_plant_harvest_entity_changes():
	TEST_CROP = Entities.Bush

	start_tick = get_tick_count()
	def plant_then_harvest():
		quick_print('plant started', get_time())
		plant(TEST_CROP)
		quick_print('plant done', get_time())
		harvest()
	drone_thread.new_thread(plant_then_harvest, East)

	plant_detected = False
	while not plant_detected:
		plant_detected = get_entity_type(East) == TEST_CROP
	quick_print('plant detected', get_time())
	plant_detected_tick = get_tick_count()

	plant_harvested = False
	while not plant_harvested:
		plant_harvested = get_entity_type(East) != TEST_CROP
	plant_harvested_tick = get_tick_count()

	while True:
		utils.print_lines([
			'plant detected after ' + str(plant_detected_tick - start_tick) + ' ticks',
			'plant no longer detected after ' + str(plant_harvested_tick - start_tick) + ' ticks',
			'plant detectable for ' + str(plant_harvested_tick - plant_detected_tick) + ' ticks'
		])


if __name__ == '__main__':
	clear()

	# test_tick_count()
	# get_unlocked_hats()
	set_execution_speed(1)
	test_plant_harvest_entity_changes()