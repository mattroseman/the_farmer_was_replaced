import utils
import crops

WORLD_SIZE = get_world_size()
FIELD_PATTERN = [
	Entities.Carrot,
	Entities.Grass,
	Entities.Tree,
]

farm_state = utils.get_farm_state_matrix()

def harvest_row(crop=Entities.Grass):
	y = get_pos_y()
	default_crop = crop
	
	for x in range(WORLD_SIZE):
		if farm_state[y][x] != None:
			crop = farm_state[y][x]
		else:
			crop = default_crop
		
		crops.CROP_HANDLERS[crop]()
		
		farm_state[y][x] = crop
		
		companion_entity, companion_pos = get_companion()
		farm_state[companion_pos[1]][companion_pos[0]] = companion_entity
		
		move(East)

# Hay : 53520 units, 10704 / minute
# Wood : 106304 units, 21260.8 / minute
def farm(should_stop=None):
	while should_stop == None or not should_stop():
		for y in range(WORLD_SIZE):
			crop = FIELD_PATTERN[y % len(FIELD_PATTERN)]
			
			harvest_row(crop)
			
			move(North)
	
if __name__ == '__main__':
	clear()
	utils.performance_test_farm(farm, 5*60)