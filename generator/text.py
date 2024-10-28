import os
import random
from random import randint

from PIL import Image, ImageDraw, ImageFont, ImageColor

from generator import sector_manager


def paste_text(img: Image, text: str,
               position_index: int,
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

    # Custom font style and font size
    text_font = ImageFont.truetype(f'{fonts_folder_path}/{font_name}',
                                   size=round(img.width / 10))
    line_spacing = 1.3

    max_width = int(img.width * 0.9)
    wrapped_text = _wrap_text(text, max_width, text_font)

    text_bbox = img_draw.textbbox((100, 100), text, text_font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    position = sector_manager.get_sector_coords(position_index, img.width, img.height, text_width, text_height)

    position = [position[0],
                position[1]]

    for line in wrapped_text:
        line_width = text_font.getlength(line)

        # Add Text to an image
        img_draw.text(((img.width - line_width) // 2,
                       position[1]),
                      text,
                      font=text_font,
                      fill=text_color,
                      stroke_fill=stroke_color,
                      stroke_width=5,
                      align=random.choice(alignments))

        position[1] += int(text_font.size * line_spacing)



    return img


def _wrap_text(text, max_width, font):
    lines = []
    words = text.split(' ')

    current_line = ''
    for word in words:
        test_line = current_line + word + ' '
        line_width = font.getlength(test_line)
        if line_width <= max_width:
            current_line = test_line
        else:
            lines.append(current_line[:-1])
            current_line = word + ' '

    lines.append(current_line[:-1])
    return lines
