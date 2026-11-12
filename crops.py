import utils

# crops states
NORMAL = 'normal'
DEAD = 'dead'
INFECTED = 'infected'
CURED = 'cured'

def set_tilled():
	if get_ground_type() != Grounds.Soil:
		till()

def set_untilled():
	if get_ground_type() != Grounds.Grassland:
		till()
	
TILLED_CROPS = [
	Entities.Carrot,
	Entities.Pumpkin
]

def water_plot():
	if num_items(Items.Water) > 1000:
		if get_water() < 1:
			use_item(Items.Water)
	else:
		if get_water() < 0.25:
			use_item(Items.Water)

def is_neighboring_tree():
	return (
		get_entity_type(North) == Entities.Tree or 
		get_entity_type(South) == Entities.Tree or
		get_entity_type(East) == Entities.Tree or
		get_entity_type(West) == Entities.Tree
	)

def is_tilled_crop(crop):
	return utils.array_contains(TILLED_CROPS, crop)
	
def get_default_handler(crop):
	def default_handler(force=False):
		if can_harvest():
			harvest()

		set_untilled()
			
		plant(crop)

		water_plot()

	return default_handler

def handle_carrot(force=False):
	if can_harvest():
		harvest()

	set_tilled()

	plant(Entities.Carrot)
	
	water_plot()
	
def handle_tree(force=False):
	if can_harvest():
		harvest()

	set_untilled()
		
	if force or not is_neighboring_tree():
		plant(Entities.Tree)
	else:
		plant(Entities.Bush)
		
	water_plot()
	
def handle_pumpkin(force=False):
	# if can_harvest():
	# 	harvest()

	set_tilled()
		
	plant(Entities.Pumpkin)
	if(force):
		use_item(Items.Fertilizer)
		use_item(Items.Fertilizer)
	while force and get_entity_type() == Entities.Dead_Pumpkin:
		plant(Entities.Pumpkin)
		use_item(Items.Fertilizer)
		use_item(Items.Fertilizer)
		
	water_plot()

def handle_sunflower(force=False, replant=True):
	if can_harvest():
		harvest()

	set_tilled()

	if replant:
		plant(Entities.Sunflower)

	water_plot()

def handle_cactus(force=False):
	if can_harvest():
		harvest()

	set_tilled()
		
	plant(Entities.Cactus)
	
	water_plot()
		
	
CROP_HANDLERS = {
	Entities.Carrot: handle_carrot,
	Entities.Grass: get_default_handler(Entities.Grass),
	Entities.Tree: handle_tree,
	Entities.Bush: get_default_handler(Entities.Bush),
	Entities.Pumpkin: handle_pumpkin
}
def get_crop_handler(crop):
	return CROP_HANDLERS[crop]

# plants a pumpkin of the given state, retrying if necessary
# WARNING: waits for pumpkin to grow
# see states above for state "enum"
def plant_pumpkin_retry(state=NORMAL):
	set_tilled()
	plant(Entities.Pumpkin)
	if state == INFECTED:
		use_item(Items.Fertilizer)
	if state == CURED:
		use_item(Items.Fertilizer)
		use_item(Items.Weird_Substance)
	while not can_harvest():
		plant(Entities.Pumpkin)
		if state == INFECTED:
			use_item(Items.Fertilizer)
		if state == CURED:
			use_item(Items.Fertilizer)
			use_item(Items.Weird_Substance)

		
if __name__ == '__main__':
	clear()
	crop_row_pattern = [Entities.Carrot, Entities.Grass, Entities.Tree]
	for y in range(get_world_size()):
		crop = crop_row_pattern[y % len(crop_row_pattern)]
		crop_handler = get_crop_handler(crop)
		
		for x in range(get_world_size()):
			crop_handler()
			move(East)
		move(North)
	
	