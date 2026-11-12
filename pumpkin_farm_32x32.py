import routines
import crops

WORLD_SIZE = get_world_size()

# like function in routines.fill_column_pumpkin(), but runs forever
# keeping drones from having to respawn
def fill_column_pumpkin(should_stop: function=None):
	pumpkin_fills_world = False

	while True:
		measurements = []

		# traverse column
		for _ in range(WORLD_SIZE):
			if should_stop():
				return

			if get_entity_type() != Entities.Pumpkin:
				crops.handle_pumpkin()

			measurement = measure()
			measurements.append(measurement)

			move(North)

		pumpkin_fills_world = len(set(measurements)) == 1
		if pumpkin_fills_world:
			harvest()

def farm(should_stop: function=None):
	routines.for_each_column_threaded(fill_column_pumpkin, should_stop)
	

if __name__ == '__main__':
	clear()
	farm()