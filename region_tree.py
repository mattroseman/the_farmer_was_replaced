import utils

WORLD_SIZE = get_world_size()

def build_node(node_zero, width, height):
	return {
		'zero': node_zero,
		'width': width,
		'height': height,
		'children': []
	}

def is_leaf(node):
	return len(node['children']) == 0

def get_area(node):
	return node['width'] * node['height']

# converts a node into the region it represents
def to_region(node):
	return {
		'zero': node['zero'],
		'width': node['width'],
		'height': node['height']
	}


# builds a world-size region_tree
def build_region_tree(region_zero, width, height):
	root = build_node(region_zero, width, height)

	return root

# builds a world-size region_tree with (0, 0) being the *center* of the node, not the zero
def build_world_region_tree():
	return build_region_tree((-WORLD_SIZE // 2, -WORLD_SIZE // 2), WORLD_SIZE, WORLD_SIZE)

def get_largest_leaf(node):
	# if no children, return node's area
	if is_leaf(node):
		return node

	# search tree for the largest node by area
	max_area = None
	largest_leaf = None 

	for child in node['children']:
		child_largest_leaf = get_largest_leaf(child)
		child_largest_area = get_area(child_largest_leaf)

		if max_area == None or child_largest_area > max_area:
			max_area = child_largest_area
			largest_leaf = child_largest_leaf

	return largest_leaf

# splits node into four sub-divisions
# attaches them to node as children
def split_node_fourths(node):
	if not is_leaf(node):
		utils.error("can't split a non-leaf node")

	if node['width'] == 1 or node['height'] == 1:
		utils.error("can't split node into fourths with height or width size 1")

	# account for uneven splits by giving north and east children the remainders
	south_height = node['height'] // 2
	north_height = node['height'] - south_height 
	west_width = node['width'] // 2
	east_width = node['width'] - west_width

	child_ne_zero = (node['zero'][0] + west_width, node['zero'][1] + south_height)
	child_nw_zero = (node['zero'][0], node['zero'][1] + south_height)
	child_se_zero = (node['zero'][0] + west_width, node['zero'][1])
	child_sw_zero = (node['zero'][0], node['zero'][1])

	node['children'] = [
		build_node(child_ne_zero, east_width, north_height),
		build_node(child_se_zero, east_width, south_height),
		build_node(child_nw_zero, west_width, north_height),
		build_node(child_sw_zero, west_width, south_height)
	]

	return node

# bisects node vertically or horizontally depending on dimensions
# attaches split nodes as children to given node
def split_node_halves(node):
	if not is_leaf(node):
		utils.error("can't split a non-leaf node")

	if node['width'] == 1 and node['height'] == 1:
		utils.error("can't split node in two with height and width size 1")

	# split vertically
	if node['height'] >= node['width']:
		south_height = node['height'] // 2
		north_height = node['height'] - south_height

		child_north_zero = (node['zero'][0], node['zero'][1] + south_height)
		child_south_zero = (node['zero'][0], node['zero'][1])

		node['children'] = [
			build_node(child_north_zero, node['width'], north_height),
			build_node(child_south_zero, node['width'], south_height)
		]
	# split horizontally
	else:
		west_width = node['width'] // 2
		east_width = node['width'] - west_width

		child_east_zero = (node['zero'][0] + west_width, node['zero'][1])
		child_west_zero = (node['zero'][0], node['zero'][1])

		node['children'] = [
			build_node(child_east_zero, east_width, node['height']),
			build_node(child_west_zero, west_width, node['height'])
		]

	return node

def split_node(node, in_fourths=True):
	if in_fourths:
		return split_node_fourths(node)
	else:
		return split_node_halves(node)

# returns all leaf-node's regions in a flat list
def flatten(node):
	if is_leaf(node):
		return [to_region(node)]

	leaf_regions = []
	for child in node['children']:
		child_leaves = flatten(child)
		for child_leaf in child_leaves:
			leaf_regions.append(to_region(child_leaf))

	return leaf_regions