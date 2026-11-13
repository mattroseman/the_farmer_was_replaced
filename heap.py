import utils

# build a max heap
def build_heap(comparator=utils.is_greater_than):
	# heaps are just arrays
	heap = {
		'comparator': comparator,
		'values': []
	}

	return heap

# gets the index of the parent in the heap, for the child at index child_i
def get_parent(child_i) -> int:
	# heap: [23, 15, 12, 13, 6]
	# child_i: 4
	# (4 - 1) // 2 = 1
	# parent of 6 at index 4 is 15 at index 1
	return (child_i - 1) // 2

# gets the indecies of the children in the heap, for a parent at index i
def get_children(parent_i) -> tuple[int, int]:
	return (2 * parent_i + 1, 2 * parent_i + 2)

def get_root(heap):
	return heap['values'][0]

def get_max(heap):
	return get_root(heap)

def bubble_up(heap, bubble_i):
	# reached root of heap
	if bubble_i <= 0:
		return heap

	bubble = heap['values'][bubble_i]

	parent_i = get_parent(bubble_i)
	parent = heap['values'][parent_i]

	# if bubble is greater than its parent, swap
	if heap['comparator'](bubble, parent):
		heap['values'][parent_i] = bubble
		heap['values'][bubble_i] = parent

		# recursively continue bubbling up, from the parent i now
		return bubble_up(heap, parent_i)
	else:
		return heap

def bubble_down(heap, bubble_i):
	heap_size = len(heap['values'])

	bubble = heap['values'][bubble_i]
	(left_child_i, right_child_i) = get_children(bubble_i)

	# if bubble has both children
	if right_child_i < heap_size:
		left_child = heap['values'][left_child_i]
		right_child = heap['values'][right_child_i]

		# if right is larger
		if heap['comparator'](right_child, left_child):
			largest_child_i = right_child_i
		else:
			# left and right are tied or left child is larger
			largest_child_i = left_child_i
	# only left child
	elif left_child_i < heap_size:
		largest_child_i = left_child_i
	# bubble is leaf node
	else:
		return heap

	# swap bubble with largest child
	if largest_child_i != None and heap['comparator'](heap['values'][largest_child_i], bubble):
		heap['values'][bubble_i] = heap['values'][largest_child_i]
		heap['values'][largest_child_i] = bubble

		return bubble_down(heap, largest_child_i)
	else:
		return heap

def pop_max(heap):
	size_heap = len(heap['values'])
	if size_heap == 0:
		return None
	if size_heap == 1:
		root = heap['values'].pop()
		return root

	root = get_root(heap)

	# replace root with last value, and bubble down
	heap['values'][0] = heap['values'].pop()
	heap = bubble_down(heap, 0)

	return root

# adds given element to the heap, maintaining sorted order
def insert(heap, elem):
	# if this is the first element of the heap
	if len(heap['values']) == 0:
		heap['values'] = [elem]
		return heap

	# add elem to end of heap and bubble up
	heap['values'].append(elem)
	heap = bubble_up(heap, len(heap['values']) - 1)

	return heap
