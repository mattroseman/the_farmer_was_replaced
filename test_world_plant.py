import crops
import utils

WORLD_SIZE = get_world_size()

# world planted in  102.2 seconds, 620866 ticks
def sing_drone_plant_world():
	for _ in range(WORLD_SIZE):
		for _ in range(WORLD_SIZE):
			till()
			plant(Entities.Sunflower)
			move(East)
		move(North)
		
# world planted in  5.19 seconds, 31533 ticks
def move_east_and_farm(position):
	move(East)
	recursive_chain_plant_world(position)
def recursive_chain_plant_world(position):
	if position[1] < WORLD_SIZE - 1:
		child = spawn_drone(move_east_and_farm, position)
	
	till()
	plant(Entities.Sunflower)
	for _ in range(WORLD_SIZE - 1):
		move(North)
		till()
		plant(Entities.Sunflower)
		
	if child:
		wait_for(child)
		
def plant_column():
	till()
	plant(Entities.Sunflower)
	for _ in range(0, WORLD_SIZE - 1):
		move(North)
		
		till()
		plant(Entities.Sunflower)

# world planted in  5.18 seconds, 31470 ticks
# probably fractionally quicker because less stack size?
# or because children are already done, so wait_for immediately returns
def spawner_drone_plant_world():
	children = set()

	for _ in range(WORLD_SIZE-1):
		child = spawn_drone(plant_column)
		children.add(child)
		move(East)
	plant_column()
	
	for child in children:
		wait_for(child)

# moves East or West spawning drones until stop x
def spawn_column_drones(direction, position, stop_x):
	children = set()

	while position[0] != stop_x:
		child = spawn_drone(plant_column)
		children.add(child)

		move(direction)
		position = utils.shift(position, direction)

	# ends on stop column
	plant_column()

	for child in children:
		wait_for(child)

def spawner_both_ways(position):
	# stop columns where drone spawner ends up
	east_stop = WORLD_SIZE // 2
	# west stop is always one right of east stop
	west_stop = (east_stop + 1) % WORLD_SIZE

	# spawn another drone spawner to move West and spawn drones
	west_drone_spawner = spawn_drone(spawn_column_drones, West, position, west_stop)

	# while you move East and spawn drones
	move(East)
	position = utils.shift(position, East)
	spawn_column_drones(East, position, east_stop)

	wait_for(west_drone_spawner)


# start_bend_y: the row where the first column will start it's bend Westward, followed by the rest
def plant_l_shape(start_position, start_bend_y=WORLD_SIZE // 2):
	crops.set_tilled()
	plant(Entities.Sunflower)
	# the farther East (+x) you are, the higher you go before turning West
	for _ in range(min(start_bend_y + start_position[0], WORLD_SIZE - 1)):
		move(North)
		crops.set_tilled()
		plant(Entities.Sunflower)

		# lookahead for already planted Sunflower
		# if get_entity_type(North) == Entities.Sunflower:
		# 	return

	# bend westward
	for _ in range(start_bend_y + start_position[0], 2*(WORLD_SIZE - 1)):
		move(West)
		crops.set_tilled()
		plant(Entities.Sunflower)

		# lookahead for already planted Sunflower
		if get_entity_type(West) == Entities.Sunflower:
			return

# world planted in  4.8 seconds, 29177 ticks
def spawner_drone_end_same_time(position):
	children = set()
	for _ in range(WORLD_SIZE - 1):
		child = spawn_drone(plant_l_shape, position, (WORLD_SIZE)*0.80 // 1)
		children.add(child)
		move(East)
		position = (position[0] + 1, position[1])

	plant_l_shape(position)

	for child in children:
		wait_for(child)

def drone_respawner(position):
	children = set()
	for _ in range(0, WORLD_SIZE-1):
		child = spawn_drone(plant_column)
		children.add(child)
		move(East)

	if max_drones() - num_drones() > 0:
		child = spawn_drone(plant_column)
		children.add(child)
		move(East)
	else:
		plant_column()
	
	for child in children:
		wait_for(child)

if __name__ == '__main__':
	clear()
	
	position = (get_pos_x(), get_pos_y())
	
	start_time = get_time()
	start_tick = get_tick_count()
	
	# world planted in  102.2 seconds, 620866 ticks
	# plant_world()

	# world planted in  5.19 seconds, 31533 ticks
	# recursive_chain_plant_world(position)

	# world planted in  5.18 seconds, 31470 ticks
	# spawner_drone_plant_world()

	# world planted in  4.8 seconds, 29177 ticks
	# spawner_drone_end_same_time(position)

	# drone_respawner(position)

	# world planted in  4.22 seconds, 25632 ticks
	spawner_both_ways(position)
	
	end_time = get_time()
	end_tick = get_tick_count()
	
	print('world planted in ', end_time - start_time, 'seconds,', end_tick-start_tick, 'ticks')