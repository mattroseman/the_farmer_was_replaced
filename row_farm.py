import utils
import drone
import crops


FIELD_PATTERN = [
	Entities.Carrot,
	Entities.Grass,
	Entities.Tree,
]

# runs through one row to harvest and replant the given crop
# drone end in same place it started
def harvest_row(crop):
	for i in range(get_world_size()):
		# till the ground for carrots, if not already tilled
		if utils.is_tilled_crop(crop) and get_ground_type() != Grounds.Soil:
			till()
		
		if can_harvest():
			harvest()
			
		# To optimize growth, Trees are interspaced with bushes
		if crop == Entities.Tree and i % 2 == 0:
			plant(Entities.Bush)
		else:
			plant(crop)
			
		crops.water_plot()
	
		move(East)

# Hay : 37056 units, 7411.2 / minute
# Wood : 53040 units, 10608 / minute
# Carrot : 14880 units, 2976 / minute
def farm(should_stop=None):
	while should_stop == None or not should_stop():
		# traverse all rows
		for y in range(get_world_size()):
			crop = FIELD_PATTERN[y % len(FIELD_PATTERN)]
			
			harvest_row(crop)				
			move(North)
			
if __name__ == '__main__':
	clear()
	utils.performance_test_farm(farm, 5 * 60)