import crops
import drone
import drone_thread

WORLD_SIZE = get_world_size()
# only sunflowers with this number of petals or less are kept, anything larger is replanted
# at the minimum of 7 every sunflower is tied for the largest, so they can be harvested in any order
MAX_SUNFLOWER_PETALS = 7

# harvests the sunflower on this plot if it's grown, then plants a new one,
# replanting until it has MAX_SUNFLOWER_PETALS petals or less
# a sunflower that's still growing is left alone
def plant_and_measure():
	crops.handle_sunflower()
	measurement = measure()
	while measurement > MAX_SUNFLOWER_PETALS:
		harvest()
		crops.handle_sunflower(True)
		measurement = measure()
	return measurement

# farms the column the drone is in, until should_stop returns True
# spawns a drone to do the same for the column to the East
def farm_column(should_stop=None):
	child = None

	# spawn a drone for the column to the East
	last_column = get_pos_x() >= (WORLD_SIZE - 1)
	if not last_column:
		child = drone_thread.new_thread(farm_column, East, should_stop)

	# the world wraps, so moving North off the top of the column
	# brings the drone back to the beginning of it
	while should_stop == None or not should_stop():
		plant_and_measure()
		move(North)

	# wait for the columns to the East to finish
	if child != None:
		wait_for(child)

def farm(should_stop: function=None):
	drone.move_to(0, 0)
	farm_column(should_stop)

if __name__ == '__main__':
	clear()
	farm()
