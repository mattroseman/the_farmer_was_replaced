import crops
import drone

DUMMY_CROPS = 10

def test():
	for _ in range(DUMMY_CROPS):
		crops.set_tilled()
		plant(Entities.Sunflower)
		while measure() > 7:
			harvest()
			plant(Entities.Sunflower)

		move(East)
	
	drone.move_to(0,1)

	crops.handle_sunflower()
	while not can_harvest():
		do_a_flip()
		
	start_power = num_items(Items.Power)
	harvest()
	end_power = num_items(Items.Power)
	print(end_power - start_power)

if __name__ == '__main__':
	clear()
	test()