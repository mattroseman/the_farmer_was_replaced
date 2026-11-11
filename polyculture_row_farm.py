import utils
import crops
import routines

WORLD_SIZE = get_world_size()
FIELD_PATTERN = [
	Entities.Carrot,
	Entities.Grass,
	Entities.Tree,
]

# if specified, polyculture farm will only plant companions for this crop type
# maximizing it's production rate
maximized_crop = Entities.Tree

# mapping of coordinates to companions, which are dicts of 'position' and 'crop'
# indicates the companion of the key'd crop
farm_companion = {}
# mapping of coordinates and the plot that coordinate is a companion to 
# (2,3): (0,0) means (2,3) is the companion of (0,0)
farm_companion_of = {}

# updates the state with this new companionship 
def update_companion(position, companion_position, companion_crop, overwrite=False):
	global farm_companion
	global farm_companion_of

	# check if the given companion is already a companion
	if companion_position in farm_companion_of:
		# do nothing if the given companion position is already companioned
		if not overwrite:
			return
		else:
			# TODO
			pass


	farm_companion[position] = {
		'position': companion_position,
		'crop': companion_crop
	}
	farm_companion_of[companion_position] = position

# wipes any state info on the companion of the given position
def wipe_companions(position):
	global farm_companion
	global farm_companion_of

	if position in farm_companion:
		companion = farm_companion.pop(position)
		farm_companion_of.pop(companion['position'])

# checks if the given position is a companion of some other plot
def is_companion(position):
	global farm_companion
	global farm_companion_of

	return position in farm_companion_of

# gets the crop the given position should have if it's a companion
def get_companion_crop(position):
	global farm_companion
	global farm_companion_of

	if position in farm_companion_of:
		companion = farm_companion[farm_companion_of[position]]
		return companion['crop']

	return None

def process_plot():
	global maximized_crop

	(x, y) = (get_pos_x(), get_pos_y())

	is_companion_crop = False
	# determine crop
	if is_companion((x, y)):
		crop = get_companion_crop((x, y))
		is_companion_crop = True
	elif maximized_crop != None:
		crop = maximized_crop
	else:
		crop = FIELD_PATTERN[y % len(FIELD_PATTERN)]

	# plant crop
	# if this is a companion crop, force the crop type
	crops.CROP_HANDLERS[crop](is_companion_crop)

	# if this plot had a previous companion, remove it
	wipe_companions((x, y))

	# calculate and record the companion of this newly planted crop
	if maximized_crop == None or crop == maximized_crop:
		companion_crop, companion_position = get_companion()
		update_companion((x, y), companion_position, companion_crop)

# Hay: 195596.8 / minute
# Wood: 678387.2 / minute
# Carrot: 92,864 / minute

def farm(should_stop=None, maximize_crop=None):
	global maximized_crop
	if maximize_crop != None:
		maximized_crop = maximize_crop

	while should_stop == None or not should_stop():
		routines.for_each_plot(process_plot)

if __name__ == '__main__':
	clear()
	utils.performance_test_farm(farm, 5*60)