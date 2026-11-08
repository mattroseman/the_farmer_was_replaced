import drone
import crops

drone.move_to(0,0)
companion = get_companion()
print(companion)
do_a_flip()

crops.handle_carrot()

companion = get_companion()
print(companion)
do_a_flip()