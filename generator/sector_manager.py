import numpy as np
import random as rnd


def _is_free(x): return x == 'free'


def get_random_free_sector(sectors, start_incl=0, stop_incl=5) -> int:
    free_sectors = np.where(_is_free(sectors))[0]
    free_sectors = [x for x in free_sectors if start_incl <= x <= stop_incl]
    choice = rnd.choice(free_sectors)
    sectors[choice] = 'occupied'
    return choice


def mark_sector_as_occupied(sectors, sector_index: int):
    sectors[sector_index] = 'occupied'


# TODO: Use this
def mark_sector_as_frame(sectors, sector_index: int):
    sectors[sector_index] = 'frame'


def get_sector_coords(sector_index,
                      whole_img_width, whole_img_height,
                      small_img_width, small_img_height,
                      random_start=-15, random_stop=20):
    x_positions = [round(whole_img_width / 50),
                   round((whole_img_width / 2) - (small_img_width / 2)),
                   (whole_img_width - small_img_width) - round(whole_img_width / 50)]

    y_positions = [round(whole_img_height / 50),
                   whole_img_height - small_img_height - rnd.randint(random_start, random_stop)]

    if sector_index in [0, 3]:
        xpos = x_positions[0]
    elif sector_index in [1, 4]:
        xpos = x_positions[1]
    elif sector_index in [2, 5]:
        xpos = x_positions[2]

    if sector_index in [0, 1, 2]:
        ypos = y_positions[0]
    elif sector_index in [3, 4, 5]:
        ypos = y_positions[1]

    return xpos, ypos
