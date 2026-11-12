import maze_thread

def enough_gold():
	return num_items(Items.Gold) >= 9863168

def maze_leaderboard():
	maze_thread.maze(enough_gold)

if __name__ == '__main__':
	maze_leaderboard()