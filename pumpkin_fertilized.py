import crops
import routines

WORLD_SIZE = get_world_size()

def plant_fertilized_pumpkin():
	crops.handle_pumpkin(True)
	
def farm():
	routines.for_each_plot(plant_fertilized_pumpkin)

if __name__ == '__main__':
	clear()
	farm()