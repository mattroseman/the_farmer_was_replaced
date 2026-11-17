import drone

drone.move_to(0, 0)

origin = (0, 0)
destination = (21, 15)


predicted = drone.quote_precise_move_cost(origin, destination)

start = get_tick_count()
drone.precise_move_to(origin, destination)
end = get_tick_count()

print('estimated', predicted, 'ticks')
print('got', end-start, 'ticks')