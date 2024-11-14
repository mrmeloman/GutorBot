from PIL import Image, ImageOps
import random, os

import generator.sector_manager as sector_manager


def paste_object(img: Image, position_index, assets_path,
                 rotation_mode="RANDOM",
                 resize_height_multiplier=0.5,
                 resize_width_multiplier=0.3):

    # Load the image
    object_path = f"{assets_path}/" + random.choice(os.listdir(assets_path))
    object_img = Image.open(object_path).convert("RGBA")

    # Resize it
    if object_img.height >= object_img.width:
        dimensions_ratio = object_img.width / object_img.height

        new_height = round(img.height * resize_height_multiplier)
        new_width = round(new_height * dimensions_ratio)

        new_size = (new_width, new_height)
        object_img = object_img.resize(new_size)
    else:
        dimensions_ratio = object_img.height / object_img.width

        new_width = round(img.width * resize_width_multiplier)
        new_height = round(new_width * dimensions_ratio)

        new_size = (new_width, new_height)
        object_img = object_img.resize(new_size)

    # Mirror it (or not, what do I care)
    if random.randint(0, 1) == 1:
        object_img = ImageOps.mirror(object_img)

    # Rotate a little
    if rotation_mode == "RANDOM":
        rotation = random.randint(-20, 20)
        object_img = object_img.rotate(rotation, expand=True)

    # Get position
    position = sector_manager.get_sector_coords(position_index,
                                                img.width, img.height)

    position = (position[0] - round(object_img.width / 2), position[1] - round(object_img.height / 2))

    print(f"Pasting an object at index {position_index}, position {position}")
    # Paste animal over background
    img.paste(object_img,
              position,
              object_img)

    return img
