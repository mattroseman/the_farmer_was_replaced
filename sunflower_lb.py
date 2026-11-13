import sunflower_thread_2

def enough_power():
	power = num_items(Items.Power)
	return power >= 100000

def sunflower_leaderboard():
	sunflower_thread_2.farm(enough_power)

if __name__ == '__main__':
	sunflower_leaderboard()