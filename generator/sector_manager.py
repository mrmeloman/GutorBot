import numpy as np
import random as rnd


def _is_free(x, ignore_objects):
    if not ignore_objects:
        return x == 'free'

    free_condition = x == 'free'
    ignore_condition = x == 'object'

    return free_condition | ignore_condition


def get_random_free_sector(sectors: np.array, start_incl=0, stop_incl=5, mark='object', ignore_objects=False) -> int:
    free_sectors = np.where(_is_free(sectors, ignore_objects))[0]
    free_sectors = [x for x in free_sectors if start_incl <= x <= stop_incl]
    choice = rnd.choice(free_sectors)
    sectors[choice] = mark
    return choice


def get_sector_coords(sector_index,
                      whole_img_width, whole_img_height):
    x_positions = [int(whole_img_width * 0.165),
                   int(whole_img_width * 0.5),
                   int(whole_img_width * 0.832)]

    y_positions = [int(whole_img_height * 0.25),
                   int(whole_img_height * 0.75)]

    if sector_index in [0, 3]:
        xpos = x_positions[0]
    elif sector_index in [1, 4]:
        xpos = x_positions[1]
    # elif sector_index in [2, 5]:
    else:
        xpos = x_positions[2]

    if sector_index in [0, 1, 2]:
        ypos = y_positions[0]
    # elif sector_index in [3, 4, 5]:
    else:
        ypos = y_positions[1]

    return xpos, ypos
