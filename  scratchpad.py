# TODO list
# try cactus sort that tracks measurements as planting, then moves largest all the way up, then second largest, and so on
#
# snake space-filling curve aadditions:
#	floor and ceiling to grab an apple on the edge, and the rest of the zig zags are within the new range
#	if apple is one East of your path, go one column over, then jacobs ladder down to fill the space
#	excursion, but you can bunch up on your way back
#
# misc:
#   try fertilizer on pumpkin farm (does it prevent dead pumpkins?)
#   weird substance farm?

import drone
set_world_size(11)
drone.wait_around()