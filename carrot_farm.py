import polyculture_row_farm

# 61504 Hay / minute
# 123660.8 Wood / minute
# 158,643 Carrot / minute
def farm_carrots():
	polyculture_row_farm.farm(None, Entities.Carrot)
	

if __name__ == '__main__':
	clear()
	farm_carrots()