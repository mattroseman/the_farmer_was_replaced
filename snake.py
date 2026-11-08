import utils
import drone

WORLD_SIZE = get_world_size()

loop = []
loop_steps = {}

# returns the sequence of positions that loop through every plot in the world
def build_hamilton_loop():
    loop = [(0,0), (0,1)]
    position = (0,1)

    for zig_zag_i in range(WORLD_SIZE // 2):
        last_zig_zag = zig_zag_i == (WORLD_SIZE // 2) - 1

        for _ in range(WORLD_SIZE - 2):
            # move North
            position = (position[0], position[1] + 1)
            loop.append(position)

        # move East
        position = (position[0] + 1, position[1])
        loop.append(position)

        for _ in range(WORLD_SIZE - 2):
            # move South
            position = (position[0], position[1] - 1)
            loop.append(position)

        if not last_zig_zag:
            # move East
            position = (position[0] + 1, position[1])
            loop.append(position)

    # move South
    position = (position[0], position[1] - 1)
    loop.append(position)

    for _ in range(WORLD_SIZE - 2):
        # move West
        position = (position[0] - 1, position[1])
        loop.append(position)

    return loop

# given a loop as a list of positions, convert it to a dictionary of each step of the loop
# where the key is a position in the loop, and the value is the next step
def convert_to_loop_steps(loop):
    loop_steps = {}

    for i in range(len(loop)):
        position = loop[i]
        next_position = loop[(i + 1) % len(loop)]

        step = utils.direction(position, next_position)

        loop_steps[position] = step

    return loop_steps

# finds where you are on the loop, and moves one step along its path
def step_along_loop():
    (x, y) = (get_pos_x(), get_pos_y())
    return move(loop_steps[(x, y)])

def snake():
    global loop
    global loop_steps

    (x, y) = (get_pos_x(), get_pos_y())
    if (x, y) not in loop_steps:
        utils.error('Drone position, (' + str(x) + ', ' + str(y) + ') is outside of loop')

    can_move = True
    while can_move:
        can_move = step_along_loop()


def farm(should_stop=None):
    global loop
    loop = build_hamilton_loop()
    global loop_steps
    loop_steps = convert_to_loop_steps(loop)

    while should_stop == None or not should_stop(): 
        drone.move_to(0, 0)
        change_hat(Hats.Dinosaur_Hat)

        start_time = get_time()
        start_inventory = utils.get_inventory()

        snake()

        change_hat(Hats.Straw_Hat)

        end_time = get_time()
        runtime = end_time - start_time
        end_inventory = utils.get_inventory()

        utils.print_lines([
            'You Won!',
            'You beat snake in ' + str(runtime // 60) + ' minutes',
            'You farmed ' + str(end_inventory[Items.Bone] - start_inventory[Items.Bone]) + ' bones'
        ])

if __name__ == '__main__':
    clear()
    farm()