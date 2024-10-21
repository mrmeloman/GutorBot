import os
import random
from random import randint

from PIL import Image, ImageDraw, ImageFont, ImageColor


def paste_text(img: Image, text: str, position_index: int,
               fonts_folder_path: str,
               h_from=0, h_to=255,
               s_from=70, s_to=100,
               v_light_from=10, v_light_to=20,
               v_dark_from=80, v_dark_to=100,
               colors_tuple=None) -> Image:

    # TODO: Better text wrapping can be done, but it's a bit complicated.
    #  See https://www.alpharithms.com/fit-custom-font-wrapped-text-image-python-pillow-552321/ as a start point

    if colors_tuple is None:
        h1 = randint(h_from, h_to)
        h2 = 255 - h1
        s1 = randint(s_from, s_to)
        s2 = min(100, (100 - s1) + randint(10, 30))

        v_light = list(range(v_light_from, v_light_to + 1))
        v_dark = list(range(v_dark_from, v_dark_to + 1))
        v_list = [v_light, v_dark]

        v_selection = random.choice(v_list)
        v_list.remove(v_selection)

        v1 = random.choice(v_selection)
        v2 = random.choice(v_list[0])

        text_color = ImageColor.getrgb(f"hsv({h1}, {s1}%, {v1}%)")
        stroke_color = ImageColor.getrgb(f"hsv({h2}, {s2}%, {v2}%)")
    else:
        text_color, stroke_color = colors_tuple

    alignments = ["left", "center", "right"]

    # Call draw Method to add 2D graphics in an image
    img_draw = ImageDraw.Draw(img)

    font_name: str = random.choice(os.listdir(fonts_folder_path))

    while " overlay." in font_name.lower():
        font_name = random.choice(os.listdir(fonts_folder_path))

    print(f"Text font: {font_name}")

    text = _random_line_breaks(text)

    # Custom font style and font size
    text_font = ImageFont.truetype(f'{fonts_folder_path}/{font_name}',
                                   size=round(img.width / 10))

    text_bbox = img_draw.textbbox((100, 100), text, text_font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    i = 0

    while text_width >= img.width:
        text = _random_line_breaks(text)

        text_font = ImageFont.truetype(f'{fonts_folder_path}/{font_name}',
                                       size=round(img.width / 10))

        text_bbox = img_draw.textbbox((100, 100), text, text_font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        if i >= 1000:
            print("i >= 1000")
            break
        else:
            i += 1

    x_offset_divider = 50
    y_offset_divider = 50

    x_positions = [img.width / x_offset_divider,
                   round((img.width / 2) - (text_width / 2)),
                   (img.width - text_width) - round(img.width / x_offset_divider)]

    y_positions = [random.randint(round(img.height / 50), round(img.height / 40)),
                   round((img.height / 2) - text_height - (text_height / y_offset_divider))]

    if position_index == 4:
        x_index = 0
        y_index = 0
    elif position_index == 5:
        x_index = 1
        y_index = 0
    elif position_index == 6:
        x_index = 2
        y_index = 0
    else:
        x_index = 1
        y_index = 1

    position = (x_positions[x_index],
                y_positions[y_index])

    # Add Text to an image
    img_draw.text(position,
                  text,
                  font=text_font,
                  fill=text_color,
                  stroke_fill=stroke_color,
                  stroke_width=5,
                  align=random.choice(alignments))

    return img


def _random_line_breaks(text: str) -> str:
    replace_probability = 0.4
    min_len = 4

    for i in range(len(text)):
        if text[i] == " ":
            if len(text[:i]) >= min_len:
                if random.random() <= replace_probability:
                    text = text[:i] + "\n" + text[i + 1:]
    return text
