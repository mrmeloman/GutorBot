import os
import random
from random import randint

from PIL import Image, ImageDraw, ImageFont, ImageColor


def paste_watermark(img: Image) -> Image:
    # Call draw Method to add 2D graphics in an image
    img_draw = ImageDraw.Draw(img)

    watermark_text = "tg: @WhatsapNightmareBot"

    text_font = ImageFont.truetype(f'assets/watermark_font.ttf',
                                   size=round(img.width / 60))

    text_bbox = img_draw.textbbox((100, 100), watermark_text, text_font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    h1 = randint(0, 255)
    h2 = 255 - h1
    s1 = randint(70, 100)
    s2 = min(100, (100 - s1) + randint(10, 30))

    v_light = list(range(10, 21))
    v_dark = list(range(80, 101))
    v_list = [v_light, v_dark]

    v_selection = random.choice(v_list)
    v_list.remove(v_selection)

    v1 = random.choice(v_selection)
    v2 = random.choice(v_list[0])

    text_color = ImageColor.getrgb(f"hsv({h1}, {s1}%, {v1}%)")
    stroke_color = ImageColor.getrgb(f"hsv({h2}, {s2}%, {v2}%)")

    x_position = 10
    y_position = img.height - text_height - 10

    position = (x_position, y_position)

    img_draw.text(position,
                  watermark_text,
                  font=text_font,
                  fill=text_color,
                  stroke_fill=stroke_color,
                  stroke_width=5,
                  align="left")

    return img
