import os
import random

from PIL import Image, ImageColor
from random import randint
from perlin_noise import PerlinNoise

import math
import numpy as np

WIDTH = 1024
HEIGHT = 768

ROUND_FACTOR = 100


def generate_plain_color(h_from=0, h_to=255,
                         s_from=15, s_to=30) -> Image:
    h = randint(0, 255)
    s = randint(15, 30)
    background_color = ImageColor.getrgb(f"hsv({h}, {s}%, 100%)")

    img = Image.new(
        mode="RGB",
        size=(WIDTH, HEIGHT),
        color=background_color)

    return img


def generate_gradient(gradient_type: str = "radial",
                      h1_from=0, h1_to=255,
                      s1_from=15, s1_to=50,
                      h2_from=0, h2_to=255,
                      s2_from=0, s2_to=20) -> Image:
    h1 = randint(h1_from, h1_to)
    s1 = randint(s1_from, s1_to)
    color1 = ImageColor.getrgb(f"hsv({h1}, {s1}%, 100%)")

    h2 = randint(h2_from, h2_to)
    s2 = randint(s2_from, s2_to)
    color2 = ImageColor.getrgb(f"hsv({h2}, {s2}%, 100%)")

    imgsize = (WIDTH, HEIGHT)

    img = Image.new(
        mode="RGB",
        size=imgsize)

    pixels = img.load()

    if gradient_type.lower() == "radial":

        half_diagonal = math.isqrt(imgsize[0] ** 2 + imgsize[1] ** 2) // 2

        for y in range(imgsize[1]):
            for x in range(imgsize[0]):
                # Find the distance to the center and make it on a scale from 0 to 1
                distance_to_center = (math.isqrt(
                    (x - imgsize[0] // 2) ** 2 + (y - imgsize[1] // 2) ** 2)) * ROUND_FACTOR // half_diagonal

                # Place r g b values to pixel (x,y)
                pixels[x, y] = (
                    (color1[0] * distance_to_center + color2[0] * (ROUND_FACTOR - distance_to_center)) // ROUND_FACTOR,
                    (color1[1] * distance_to_center + color2[1] * (ROUND_FACTOR - distance_to_center)) // ROUND_FACTOR,
                    (color1[2] * distance_to_center + color2[2] * (ROUND_FACTOR - distance_to_center)) // ROUND_FACTOR)

    elif gradient_type.lower() == "rect":
        half_width = imgsize[0] // 2

        for y in range(imgsize[1]):
            for x in range(imgsize[0]):
                # Find the distance to the closest edge
                distance_to_edge = min(abs(x - imgsize[0]), x, abs(y - imgsize[1]), y)

                # Make it on a scale from 0 to 1
                distance_to_edge = distance_to_edge * ROUND_FACTOR // half_width

                # Write r g b values to pixel x, y
                pixels[x, y] = (
                (color1[0] * distance_to_edge + color2[0] * (ROUND_FACTOR - distance_to_edge)) // ROUND_FACTOR,
                (color1[1] * distance_to_edge + color2[1] * (ROUND_FACTOR - distance_to_edge)) // ROUND_FACTOR,
                (color1[2] * distance_to_edge + color2[2] * (ROUND_FACTOR - distance_to_edge)) // ROUND_FACTOR)

    elif gradient_type.lower() == "horizontal":
        # Make output image
        arr = np.zeros((HEIGHT, WIDTH, 3), np.uint8)

        # Fill R, G and B channels with linear gradient between two end colours
        arr[:, :, 0] = np.linspace(color1[0], color2[0], WIDTH, dtype=np.uint8)
        arr[:, :, 1] = np.linspace(color1[1], color2[1], WIDTH, dtype=np.uint8)
        arr[:, :, 2] = np.linspace(color1[2], color2[2], WIDTH, dtype=np.uint8)

        img = Image.fromarray(arr)

    return img


def make_bg_from_image(images_folder_path, user_image: Image = None) -> Image:
    if user_image is None:
        # Pick and load the background image
        bg_image_path: str = f"{images_folder_path}/{random.choice(os.listdir(images_folder_path))}"
        bg_image = Image.open(bg_image_path).convert("RGBA")
    else:
        bg_image = user_image

    # Resize it
    bg_image = bg_image.resize((WIDTH, HEIGHT))

    return bg_image


def perlin() -> Image:
    img = generate_plain_color()

    h = randint(0, 255)

    x = 0
    y = 0

    noise1 = PerlinNoise(octaves=3)
    noise2 = PerlinNoise(octaves=6)
    noise3 = PerlinNoise(octaves=12)
    noise4 = PerlinNoise(octaves=24)

    while x < WIDTH:
        y = 0
        while y < HEIGHT:
            value = noise1([x / WIDTH, y / HEIGHT])
            value += 0.5 * noise2([x / WIDTH, y / HEIGHT])
            value += 0.25 * noise3([x / WIDTH, y / HEIGHT])
            value += 0.125 * noise4([x / WIDTH, y / HEIGHT])
            value = ((value + 1) / 2) * 50
            color = ImageColor.getrgb(f"hsv({h}, {value}%, 100%)")
            img.putpixel(
                (x, y),
                color)
            y += 1
        x += 1

    return img
