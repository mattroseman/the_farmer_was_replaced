import utils
import drone

import polyculture_row_farm
import sunflower_farm
import pumpkin_farm
import cactus_farm

def is_enough_power():
	inventory = utils.get_inventory()
	power = inventory[Items.Power]
	
	return power >= 20000
def is_not_enough_power():
	return not is_enough_power()
	
def is_enough_hay_wood_carrots():
	inventory = utils.get_inventory()
	hay = inventory[Items.Hay]
	wood = inventory[Items.Wood]
	carrots = inventory[Items.Carrot]
	
	return hay >= 100000 and wood >= 100000 and carrots >= 100000
def is_not_enough_hay_wood_carrots():
	return not is_enough_hay_wood_carrots()

def is_enough_pumpkins():
	inventory = utils.get_inventory()
	pumpkins = inventory[Items.Pumpkin]
	
	return pumpkins >= 1000000
def is_not_enough_pumpkins():
	return not is_enough_pumpkins()
	
def resources_needed():
	return is_not_enough_power() or is_not_enough_hay_wood_carrots() or is_not_enough_pumpkins()
def pumpkin_resources_needed():
	return is_not_enough_power() or is_not_enough_hay_wood_carrots()
	
# combines a resource_check function with a timer,
# so even if the resource_check passes, a minimum time will run
def get_resource_check_with_timer(resource_check, time_limit):
	state = [utils.get_timer(time_limit)]
	
	def resource_check_with_timer():
		timer = state[0]
	
		return resource_check() and timer()
	
	return resource_check_with_timer

def main():
	while True:
		clear()
		drone.move_to(0,0)
		
		if is_not_enough_power():
			sunflower_farm.farm(get_resource_check_with_timer(is_enough_power, 5*60))
		elif is_not_enough_hay_wood_carrots():
			polyculture_row_farm.farm(get_resource_check_with_timer(is_enough_hay_wood_carrots, 5*60))
		elif is_not_enough_pumpkins():
			pumpkin_farm.farm(pumpkin_resources_needed)
		else:
			cactus_farm.farm_once(resources_needed)
		

if __name__ == '__main__':
	clear()
	main()