# TODO list
# try cactus sort that tracks measurements as planting, then moves largest all the way up, then second largest, and sog
#
# snake space-filling curve aadditions:
#	floor and ceiling to grab an apple on the edge, and the rest of the zig zags are within the new range
#	if apple is one East of your path, go one column over, then jacobs ladder down to fill the space
#	excursion, but you can bunch up on your way back


import drone
import polyculture_row_farm

# go for pumpkin yield unlock
cost = get_cost(Unlocks.Pumpkins)

cost_carrots = cost[Items.Carrot]
have_carrots = num_items(Items.Carrot)

def have_enough_carrots():
	have_carrots = num_items(Items.Carrot)
	return have_carrots >= cost_carrots + 100000

drone.move_to(0, 2)
print('Have', have_carrots, 'carrots')
move(South)
print('Need', cost_carrots - have_carrots + 100000, 'carrots')
move(South)

polyculture_row_farm.farm(have_enough_carrots, Entities.Carrot)

unlock(Unlocks.Pumpkins)