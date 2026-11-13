# Divisible Load Partitioner

import utils
import region_tree

# # partition loads splits the given items list into partitions of diminishing size
# # this is to better divide labor, where the first partition has more work, and each one after diminishes in size
# def partition_load(items: list, num_partitions: int):
# 	num_items = len(items)
# 	num_partitions = min(num_items, num_partitions)
# 
# 	if num_partitions == 1:
# 		return [items]
# 
# 	partition_sizes = []
# 	num_partitioned = 0
# 	for _ in range(num_partitions):
# 		size = 1
# 		partition_sizes.append(size)
# 		num_partitions += 1
# 
# 	while num_partitioned <= num_items:
# 		for i in range(num_partitions):
# 			for j in range(num_partitions - i):
# 				partition_sizes[j] += 1
# 				num_partitions += 1
# 
# 	partitions = []
# 	i = 0
# 	for partition_size in partition_sizes:
# 		partitions.append(items[i:partition_size])

# returns the elements in the arithmetic sequence, from start inclusive up to stop exclusive
# with the starting step size
def get_arithmetic_sequence(start=0, starting_step_size=10, stop=100) -> list:
	index = start
	step_size = starting_step_size
	arithmetic_sequence = []

	while index < stop:
		arithmetic_sequence.append(index)
		index += step_size
		step_size += 1

	return arithmetic_sequence

# partition items off of an arithmetic sequence,
# e.g. partition sizes of 10, 11, 13, 16, 20, 25...
def front_weighted_partition_load(items: list, smallest_partition: int=10) -> list[list]:
	num_items = len(items)

	# get arithmetic sequence representing partition borders
	# sequence goes up, so larger and larger partitions
	border_indecies = get_arithmetic_sequence(0, smallest_partition, num_items)
	border_indecies.append(len(items))

	# for a frontweighted load, reverse partition borders, so they get smaller and smaller
	partition_indecies = utils.reverse_list(border_indecies)
	num_partitions = len(partition_indecies)

	partitions = []
	# for each partition's start, grab the items until the next partition's start
	# i.e. the partition
	for index_index in range(num_partitions - 1):
		end_i = partition_indecies[index_index]
		start_i = partition_indecies[index_index + 1]
		partitions.append(items[start_i:end_i])

	# check if the first partition (last in the original sequence, with the remainders)
	# is smaller than the second partition (was second to last in original indecies)
	if num_partitions > 2:
		len_first_partition = len(partitions[0])
		if len_first_partition < len(partitions[1]):
			# redistribute the last partition's items into the rest of the partitions
			first_partition = partitions[0]

			# remove first partition
			partitions = partitions[1:]

			# redistribute
			for i in range(len_first_partition):
				partitions[(i % (num_partitions - 1)) + 1].append(first_partition[i])

	return partitions

LARGEST_SMALLEST_PARTITION_RATIO = 0.4

# partition the items off of the arithmetic series: each next partition smaller by a constant size
# e.g. partition sizes 16, 14, 12, 10, 8 
def front_loaded_partition(items: list, num_partitions: int):
	num_items = len(items)
	num_partitions = min(num_items, num_partitions)

	if num_partitions == 1 or num_items <= 1:
		return [items]

	# Sum of arithmetic series based off the first and last elements 
	# S = num_partitions * (len_first_partition + len_last_partition) / 2
	# or the ratio
	# S = num_parititions * (len_fist_partition + len_first_partition * ratio) / 2
	# S = num_partitions * len_first_partition * (1 + ratio) / 2
	# solve for len_first_partition
	# len_first_partition = 2*S / (num_partitions * (1 + ratio))
	# where S is really the num_items, i.e. if you add the sizes of each partition up, you get the whole list size
	len_first_partition = 2 * num_items / (num_partitions * (1 + LARGEST_SMALLEST_PARTITION_RATIO))
	len_last_partition = len_first_partition * LARGEST_SMALLEST_PARTITION_RATIO
	common_difference = (len_first_partition - len_last_partition) / (num_partitions - 1)

	partitions = []

	partition_len = len_first_partition
	partition_start = 0
	for i in range(num_partitions):
		last_partition = i == num_partitions - 1

		partition_start_rounded = partition_start // 1

		if not last_partition:
			end_rounded = (partition_start + partition_len) // 1
			partitions.append(items[partition_start_rounded:end_rounded])
		else:
			partitions.append(items[partition_start_rounded:])
		partition_start += partition_len
		partition_len = partition_len - common_difference

	return partitions

# returns a list of lists, that is an even partition of items
def partition(items: list, num_partitions: int) -> list[list]:
	len_items = len(items)
	partition_size = len_items // num_partitions
	remainder = len_items % num_partitions

	partition_starts = range(0, partition_size * num_partitions, partition_size)

	partitions = []
	for i in range(num_partitions):
		partition_start = partition_starts[i]
		if i < num_partitions - 1:
			partition_end = partition_starts[i+1]
		else:
			partition_end = len_items

		partitions.append(items[partition_start:partition_end])

	return partitions

# returns a list of partitions of the given region
# each partition is a dictionary like: 
# {
#   zero: (0, 0),
#   width: 10
#   height: 10
# }
# where the rectangular partitioned regions constitute the given starting region
# partitions should be roughly equal size, but with likely variations
def region_partition(region_zero, width, height, num_partitions):
	partitions_root = region_tree.build_region_tree(region_zero, width, height)

	region_area = region_tree.get_area(partitions_root)
	if num_partitions > region_area:
		utils.error("can't partition region of area " + str(region_area) + " into " + str(num_partitions) + " partitions")

	# repeatedly bisect the largest partitions until the goal number of partitions is reached
	partitions_remaining = num_partitions - 1
	while partitions_remaining > 0:
		# get the largest partition
		largest_partition = region_tree.get_largest_leaf(partitions_root)
		# split it in half
		region_tree.split_node_halves(largest_partition)
		partitions_remaining -= 1

	partition_list = region_tree.flatten(partitions_root)

	return partition_list


