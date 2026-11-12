import routines
import drone

import pumpkin_farm_32x32
import pumpkin_thread

def pumpkin_leaderboard():
	def enough_pumpkins():
		pumpkins_harvested = num_items(Items.Pumpkin)
		return pumpkins_harvested >= 200000000

	# pumpkin_farm_32x32.farm(enough_pumpkins)
	pumpkin_thread.farm(enough_pumpkins)

if __name__ == '__main__':
	pumpkin_leaderboard()