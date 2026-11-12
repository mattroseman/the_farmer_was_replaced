import utils
import crops
import drone
import routines

def test_pumpkin():
	crops.plant_pumpkin_retry()

	start_inventory = utils.get_inventory()
	harvest()
	end_inventory = utils.get_inventory()

	print('Pumpkin Yield:', end_inventory[Items.Pumpkin] - start_inventory[Items.Pumpkin])

def test_infected_pumpkin():
	crops.plant_pumpkin_retry(crops.INFECTED)

	start_inventory = utils.get_inventory()
	harvest()
	end_inventory = utils.get_inventory()

	print('Infected Pumpkin Yield:', end_inventory[Items.Pumpkin] - start_inventory[Items.Pumpkin])

def test_cured_pumpkin():
	crops.plant_pumpkin_retry(crops.CURED)

	start_inventory = utils.get_inventory()
	harvest()
	end_inventory = utils.get_inventory()

	print('Cured Pumpkin Yield:', end_inventory[Items.Pumpkin] - start_inventory[Items.Pumpkin])

def test_four_pumpkin():
	crops.plant_pumpkin_retry()
	move(East)
	crops.plant_pumpkin_retry()
	move(North)
	crops.plant_pumpkin_retry()
	move(West)
	crops.plant_pumpkin_retry()
	move(South)

	start_inventory = utils.get_inventory()
	harvest()
	end_inventory = utils.get_inventory()

	print('2x2 Pumpkin Yield:', end_inventory[Items.Pumpkin] - start_inventory[Items.Pumpkin])

def test_partially_infected_four_pumpkin():
	crops.plant_pumpkin_retry(crops.INFECTED)
	move(East)
	crops.plant_pumpkin_retry()
	move(North)
	crops.plant_pumpkin_retry()
	move(West)
	crops.plant_pumpkin_retry()
	move(South)

	start_inventory = utils.get_inventory()
	harvest()
	end_inventory = utils.get_inventory()

	print('Partially Infected 2x2 Pumpkin Yield:', end_inventory[Items.Pumpkin] - start_inventory[Items.Pumpkin])

def test_fully_infected_four_pumpkin():
	crops.plant_pumpkin_retry(crops.INFECTED)
	move(East)
	crops.plant_pumpkin_retry(crops.INFECTED)
	move(North)
	crops.plant_pumpkin_retry(crops.INFECTED)
	move(West)
	crops.plant_pumpkin_retry(crops.INFECTED)
	move(South)

	start_inventory = utils.get_inventory()
	harvest()
	end_inventory = utils.get_inventory()

	print('Fully Infected 2x2 Pumpkin Yield:', end_inventory[Items.Pumpkin] - start_inventory[Items.Pumpkin])

def test_nine_pumpkin():
	for y in range(3):
		drone.move_to(0, y)
		for _ in range(3):
			crops.plant_pumpkin_retry()
			move(East)

	drone.move_to(0, 0)

	start_inventory = utils.get_inventory()
	harvest()
	end_inventory = utils.get_inventory()

	print('3x3 Pumpkin Yield:', end_inventory[Items.Pumpkin] - start_inventory[Items.Pumpkin])

def test_partially_infected_nine_pumpkin():
	crops.plant_pumpkin_retry(crops.INFECTED)
	for y in range(3):
		for x in range(3):
			drone.move_to(x, y)
			crops.plant_pumpkin_retry()

	drone.move_to(0, 0)

	start_inventory = utils.get_inventory()
	harvest()
	end_inventory = utils.get_inventory()

	print('Partially Infected 3x3 Pumpkin Yield:', end_inventory[Items.Pumpkin] - start_inventory[Items.Pumpkin])

def test_fully_infected_nine_pumpkin():
	crops.plant_pumpkin_retry(crops.INFECTED)
	for y in range(3):
		for x in range(3):
			drone.move_to(x, y)
			crops.plant_pumpkin_retry(crops.INFECTED)

	drone.move_to(0, 0)

	start_inventory = utils.get_inventory()
	harvest()
	end_inventory = utils.get_inventory()

	print('Fully Infected 3x3 Pumpkin Yield:', end_inventory[Items.Pumpkin] - start_inventory[Items.Pumpkin])
	

# pumpkin: 128
# infected pumpkin: 64
# cured pumpkin: 128
#
# 2x2 pumpkin: 1024
# partially infected 2x2 pumpkin: 896
# fully infected 2x2 pumpkin: 512
#
# 3x3 pumpkin: 3456
# partially infected 3x3 pumpkin: 3264
# fully infected 3x3 pumpkin: 1728
def test():
	test_cases = [
		# test_pumpkin,
		# test_infected_pumpkin,
		# test_cured_pumpkin,
		# test_four_pumpkin,
		# test_partially_infected_four_pumpkin,
		# test_fully_infected_four_pumpkin,
		test_nine_pumpkin,
		test_partially_infected_nine_pumpkin,
		test_fully_infected_nine_pumpkin
	]

	for test_case in test_cases:
		test_case()
		do_a_flip()

	drone.move_to(0, 0)


if __name__ == '__main__':
	clear()

	# routines.till_world()
	# test()
	routines.fill_world_pumpkin()

	drone.wait_around()