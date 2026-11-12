import sunflower_thread

def enough_power():
	power = num_items(Items.Power)
	return power >= 100000

def sunflower_leaderboard():
	sunflower_thread.farm(enough_power)

if __name__ == '__main__':
	sunflower_leaderboard()