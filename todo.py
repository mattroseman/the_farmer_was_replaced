# TODO: sunflowers / partitioner
#
# 1. Last 9 sunflowers get no 8x bonus (need >= 10 on farm; check 9 vs 10).
#    - Option A: drop 9 positions from the smallest level(s) before partitioning.
#    - Option B: reserve 9-10 never-harvested 7-petal plots in the (0, 0) region.
#
# 2. Grow-time test: min / max / avg crop grow time, like the crop-yield test.
#
# 3. Main drone harvests too: 32 regions (8x4), main drone takes the nearest
#    one each level. Regenerate cache.py.
#
# 4. Angular partitioning: split positions into slope-sorted wedges, equal tile
#    counts per drone (no atan2, so compare slopes / cross products).
#
# 5. Synced harvesting with no return between petal-counts
#		- drones plant their crop, based on each measurement's spacing, estimates time to harvest
#		then every drone returns, and max estimated harvest time/measurement is shared
#		- drones can then plant independently and have shared schedule
#     
# 6. try merging sorted position with improved merge_sorted() function
