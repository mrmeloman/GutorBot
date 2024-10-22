import os
import random
from random import randint

from PIL import Image, ImageDraw, ImageFont, ImageColor


def paste_watermark(img: Image) -> Image:
    watermark_img = Image.open("assets/watermark.png").convert("RGBA")

    dimensions_ratio = watermark_img.height / watermark_img.width

    new_width = round(img.width * 0.3)
    new_height = round(new_width * dimensions_ratio)

    new_size = (new_width, new_height)
    watermark_img = watermark_img.resize(new_size)

    x_position = 10
    y_position = img.height - watermark_img.height + 20

    position = (x_position, y_position)

    img.paste(watermark_img,
              position,
              watermark_img)

    return img
