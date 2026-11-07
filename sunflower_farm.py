import utils
import crops
import drone

WORLD_SIZE = get_world_size()
MAX_PETALS = 15
MIN_PETALS = 7

sunflower_petals = {}

def harvest_sunflowers():
	for num_petals in range(MAX_PETALS, MIN_PETALS-1, -1):
		if num_petals not in sunflower_petals:
			continue
		
		for (x, y) in sunflower_petals[num_petals]:
			drone.move_to(x, y)
			crops.handle_sunflower(False)
		sunflower_petals[num_petals] = []

	drone.move_to(0, 0)

def farm(should_stop=None):
	while should_stop == None or not should_stop():
		for y in range(WORLD_SIZE):
			for x in range(WORLD_SIZE):
				crops.handle_sunflower()

				num_petals = measure()
				if num_petals in sunflower_petals:
					sunflower_petals[num_petals].append((x, y))
				else:
					sunflower_petals[num_petals] = [(x, y)]

				move(East)
			move(North)

		harvest_sunflowers()


if __name__ == '__main__':
	clear()
	utils.performance_test_farm(farm, 5*60)