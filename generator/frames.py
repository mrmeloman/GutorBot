import os
import random

from PIL import Image, ImageOps


def paste_frame(img: Image, assets_path: str, frame_type: int = 1):
    if 2 <= frame_type <= 5:  # Side frames
        frame_path = f"{assets_path}/side/{random.choice(os.listdir(f'{assets_path}/side'))}"
        frame_img = Image.open(frame_path).convert("RGBA")

        if frame_type == 2:  # Left side

            new_height = img.height
            new_width = round((frame_img.width * new_height) / frame_img.height)
            new_size = (new_width, new_height)
            frame_img = frame_img.resize(new_size)

            frame_position = (0, 0)

        elif frame_type == 3:  # Right side

            frame_img = ImageOps.mirror(frame_img)

            new_height = img.height
            new_width = round((frame_img.width * new_height) / frame_img.height)
            new_size = (new_width, new_height)
            frame_img = frame_img.resize(new_size)

            frame_position = (img.width - frame_img.width, 0)

        elif frame_type == 4:  # Top

            frame_img = frame_img.rotate(270, expand=True)

            new_width = img.width
            new_height = round((frame_img.height * new_width) / frame_img.width)
            new_size = (new_width, new_height)
            frame_img = frame_img.resize(new_size)

            frame_position = (0, 0)

        else:  # Bottom

            frame_img = frame_img.rotate(90, expand=True)

            new_width = img.width
            new_height = round((frame_img.height * new_width) / frame_img.width)
            new_size = (new_width, new_height)
            frame_img = frame_img.resize(new_size)

            frame_position = (0, img.height - frame_img.height)
    elif 6 <= frame_type <= 9:  # Corner frames
        frame_path = f"{assets_path}/corner/{random.choice(os.listdir(f'{assets_path}/corner'))}"
        frame_img = Image.open(frame_path).convert("RGBA")

        # Resize it
        dimensions_ratio = frame_img.width / frame_img.height

        new_height = round(img.height * 0.7)
        new_width = round(new_height * dimensions_ratio)

        new_size = (new_width, new_height)
        frame_img = frame_img.resize(new_size)

        frame_offset_percentage = 3

        if frame_type == 6:  # Top left
            frame_position = (0 - round((img.width * frame_offset_percentage) / 100),
                              0 - round((img.height * frame_offset_percentage) / 100))
        elif frame_type == 7:  # Top Right
            frame_img = ImageOps.mirror(frame_img)
            frame_position = ((img.width - frame_img.width) + round((img.width * frame_offset_percentage) / 100),
                              0 - round((img.height * frame_offset_percentage) / 100))
        elif frame_type == 8:  # Bottom left
            frame_img = ImageOps.flip(frame_img)
            frame_position = (0 - round((img.width * frame_offset_percentage) / 100),
                              (img.height - frame_img.height) + round((img.height * frame_offset_percentage) / 100))
        else:  # Bottom right
            frame_img = ImageOps.flip(frame_img)
            frame_img = ImageOps.mirror(frame_img)

            frame_position = ((img.width - frame_img.width) + round((img.width * frame_offset_percentage) / 100),
                              (img.height - frame_img.height) + round((img.height * frame_offset_percentage) / 100))
    else:  # Whole frames
        frame_path = f"{assets_path}/whole/{random.choice(os.listdir(f'{assets_path}/whole'))}"
        frame_img = Image.open(frame_path)

        frame_overshoot_percentage = 10

        frame_size = (img.width + round(img.width / frame_overshoot_percentage),
                      img.height + round(img.height / frame_overshoot_percentage))

        frame_img = frame_img.resize(frame_size)
        frame_position = (0 - round(img.width / (frame_overshoot_percentage * 2)),
                          0 - round(img.height / (frame_overshoot_percentage * 2)))

        # Mirror it (or not, what do I care)
        if random.randint(0, 1) == 1:
            frame_img = ImageOps.mirror(frame_img)

    img.paste(frame_img,
              frame_position,
              frame_img)

    return img
