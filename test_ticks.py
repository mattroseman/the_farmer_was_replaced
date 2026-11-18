set_world_size(5)

import drone

WORLD_SIZE = get_world_size()

clear()

# 0 ticks
# start = get_tick_count()
# get_time()
# end = get_tick_count()
# print('get_time():', end-start, 'ticks')

# 0 ticks
# x = 5
# y = None
# start = get_tick_count()
# y = x
# end = get_tick_count()
# print('variable assignment:', end - start, 'ticks')
# do_a_flip()

# 0 ticks
# x = 5
# start = get_tick_count()
# y = x
# end = get_tick_count()
# print('variable creation & assignment:', end - start, 'ticks')
# do_a_flip()

# 0 ticks
# end = [0]
# def foobar():
# 	end[0] = get_tick_count()
# start = get_tick_count()
# result = foobar()
# print('function call:', end[0] - start, 'ticks')
# do_a_flip()

# 0 ticks
# a = 5
# end = [0]
# def foobar(a):
# 	b = a
# 	end[0] = get_tick_count()
# start = get_tick_count()
# result = foobar(a)
# print('function call with argument:', end[0] - start, 'ticks')
# do_a_flip()

# 0 ticks
# def foobar():
# 	return
# start = get_tick_count()
# foobar()
# end = get_tick_count()
# print('function return:', end - start, 'ticks')
# do_a_flip()

# 1 tick
# start = get_tick_count()
# tuple = (10, 15)
# end = get_tick_count()
# print('tuple creation:', end - start, 'ticks')
# do_a_flip()

# 0 ticks
# tuple = (10, 15)
# start = get_tick_count()
# (a, b) = tuple
# end = get_tick_count()
# print('tuple unpacking:', end - start, 'ticks')
# do_a_flip()

# 1 tick
# start = get_tick_count()
# drone.do_nothing()
# end = get_tick_count()
# print('drone.do_nothing():', end - start, 'ticks')
# do_a_flip()

# 1 tick
# start = get_tick_count()
# pass
# end = get_tick_count()
# print('pass:', end - start, 'ticks')

# 1 tick
# x = 0
# y = 1
# start = get_tick_count()
# x != y
# end = get_tick_count()
# print('conditional:', end - start, 'ticks')
# do_a_flip()

# 1 tick
# start = get_tick_count()
# if True:
# 	get_time()
# end = get_tick_count()
# print('if statement:', end - start, 'ticks')
# do_a_flip()

# x = 0
# y = 1
# start = get_tick_count()
# if x != y:
# 	get_time()
# end = get_tick_count()
# print('conditional if statement:', end - start, 'ticks')
# do_a_flip()

# x = [1, 2, 3]
# start = get_tick_count()
# x[1]
# end = get_tick_count()
# print('x[1]:', end - start, 'ticks')
# do_a_flip()

# x = [1, 2, 3]
# start = get_tick_count()
# _, a, _ = x
# end = get_tick_count()
# print('unpack from list:', end - start, 'ticks')
# do_a_flip()

# 1 tick
# l = [1, 2, 3]
# start = get_tick_count()
# for i in l:
# 	end = get_tick_count()
# 	break
# print('enter for loop:', end - start, 'ticks')

# 1 tick
# l = []
# start = get_tick_count()
# for i in l:
# 	get_time()
# end = get_tick_count()
# print('unentered for loop:', end-start, 'ticks')

# 1 tick
# start = get_tick_count()
# while True:
# 	end = get_tick_count()
# 	break
# print('enter while loop:', end - start, 'ticks')

# # 1 tick
# start = get_tick_count()
# 4 % 3
# end = get_tick_count()
# print('modular operator:', end - start, 'ticks')
# 
# # 2 ticks
# start = get_tick_count()
# (1 + 3) % 3
# end = get_tick_count()
# print('nested operators (1 + 3) % 3:', end - start, 'ticks')
# 
# # 6 ticks
# start = get_tick_count()
# if (6 - 1) % 2 < (9 - 1) % 2:
# 	pass
# end = get_tick_count()
# print('if (6 - 1) % 2 < (9 - 1) % 2:', end - start, 'ticks')
# 
# # 0 ticks
# start = get_tick_count()
# WORLD_SIZE
# end = get_tick_count()
# print('reference global:', end - start, 'ticks')

# ======== MOVEMENT ========

# 200 ticks
# start = get_tick_count()
# move(East)
# end = get_tick_count()
# print('move():', end - start, 'ticks')
# move(West)
# do_a_flip()

# 228 ticks
# start = get_tick_count()
# drone.move_to(0, 1)
# end = get_tick_count()
# print('drone.move_to():', end - start, 'ticks')
# drone.move_to(0, 0)
# do_a_flip()

# 1 tick
# start = get_tick_count()
# range(10)
# end = get_tick_count()
# print('range(10):', end-start, 'ticks')
# start = get_tick_count()
# range(1000,-1,-5)
# end = get_tick_count()
# print('range(1000,-1,-5):', end-start, 'ticks')

# 2 ticks
# start = get_tick_count()
# for _ in range(0):
# 	get_time()
# end = get_tick_count()
# print('for loop w/ range:', end-start, 'ticks')

# 1 tick
# start = get_tick_count()
# if 0:
# 	get_time()
# end = get_tick_count()
# print('if number:', end-start, 'ticks')

# 0 ticks
# start = get_tick_count()
# not False
# end = get_tick_count()
# print('not:', end-start, 'ticks')

# 1 tick
d = {'a': 7 }
start = get_tick_count()
d['a']
end = get_tick_count()
print('reference dict:', end-start, 'ticks')

# 3 ticks
d = {'a': { 'b': { 'c': 7 } } }
start = get_tick_count()
d['a']['b']['c']
end = get_tick_count()
print('reference 3-nested dict:', end-start, 'ticks')

# 1 tick
l = ['a', 'b', 'c']
start = get_tick_count()
l[1]
end = get_tick_count()
print('reference list', end-start, 'ticks')


# 212 ticks
# a = (0, 0)
# b = (0, 1)
# start = get_tick_count()
# drone.precise_move_to(a, b)
# end = get_tick_count()
# print('drone.precise_move_to():', end - start, 'ticks')
# drone.precise_move_to((0, 1), (0, 0))
# do_a_flip()
