time_action = 5
time_turn = 5
time_turn_for_human=2

game_id = 1 #iki game_id var biri processlerin idleri diğeri loop id burdaki loop id
#random_seed = 444

import random
def random_seed(fixed_random=True):
    if fixed_random:
        random_seed = 444
        return random_seed
    else:
        return random.randint(0, 100)