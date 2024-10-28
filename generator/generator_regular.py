import datetime
import random

from generator import sector_manager, bgen, frames, text, user_images, watermark, overlay
from generator.object import paste_object
import numpy as np

STYLE_FOLDER_NAME = "regular"


async def generate_regular(query: str, usr_image=None, is_png=False):
    skip_watermark = False

    if query == "---noquery---":
        query = ""

    sectors = np.array(['free', 'free', 'free',
                        'free', 'free', 'free'])

    # === RANDOM PARAMETERS ===
    print("Setting random parameters")
    bg_option = random.randint(1, 3)
    frame_type = random.randint(1, 9)

    # === BACKGROUND ===
    print("Generating random background of type: ", end="")
    if bg_option == 1:
        print("picture")
        img = bgen.make_bg_from_image(images_folder_path=f"assets/{STYLE_FOLDER_NAME}/backgrounds")
    elif bg_option == 2:
        gradient_type = random.choice(['radial', 'rect', 'horizontal'])
        print(f"{gradient_type} gradient")
        img = bgen.generate_gradient(gradient_type)
    else:
        print("solid colour")
        img = bgen.generate_plain_color()

    # === FLOWERS ===
    flowers_position_index = sector_manager.get_random_free_sector(sectors, 3, 5)
    img = paste_object(img, flowers_position_index, f"assets/{STYLE_FOLDER_NAME}/flowers")

    # === FRAME ===
    img = frames.paste_frame(img, f"assets/{STYLE_FOLDER_NAME}/frames", frame_type)

    if frame_type == 6:
        img = frames.paste_frame(img, f"assets/{STYLE_FOLDER_NAME}/frames", 9)
    elif frame_type == 7:
        img = frames.paste_frame(img, f"assets/{STYLE_FOLDER_NAME}/frames", 8)
    elif frame_type == 8:
        frame_type = 7
        img = frames.paste_frame(img, f"assets/{STYLE_FOLDER_NAME}/frames", frame_type)
    elif frame_type == 9:
        frame_type = 6
        img = frames.paste_frame(img, f"assets/{STYLE_FOLDER_NAME}/frames", frame_type)
    elif frame_type == 2:
        img = frames.paste_frame(img, f"assets/{STYLE_FOLDER_NAME}/frames", 3)
    elif frame_type == 3:
        img = frames.paste_frame(img, f"assets/{STYLE_FOLDER_NAME}/frames", 2)

    print(f"Pasting frame of type index: {frame_type}")

    # === ANIMAL ===
    animal_folders = ["animals", "frogs"]
    now = datetime.datetime.now(datetime.timezone.utc)
    if now.weekday() == 2:
        animal_folder_choice = random.choices(animal_folders, [0.7, 0.3])
        animal_folder_name = animal_folder_choice[0]
    else:
        animal_folder_name = animal_folders[0]

    animal_position_index = sector_manager.get_random_free_sector(sectors, 3, 5)
    img = paste_object(img, animal_position_index, f"assets/{STYLE_FOLDER_NAME}/{animal_folder_name}")

    # === OBJECT ===
    objects_position_index = sector_manager.get_random_free_sector(sectors)
    img = paste_object(img, objects_position_index, f"assets/{STYLE_FOLDER_NAME}/objects")

    # === USER IMAGE ===
    if usr_image is not None:
        user_image_position_index = sector_manager.get_random_free_sector(sectors)
        img = user_images.paste_user_image(img, usr_image, user_image_position_index, is_png=is_png)

    # === VIGNETTE ===
    print("Pasting vignette")
    img = overlay.paste_overlay(img, f"assets/{STYLE_FOLDER_NAME}/vignettes")

    # === TEXT ===
    print(f"Pasting text")
    text_position_index = sector_manager.get_random_free_sector(sectors)
    img = text.paste_text(img, query, text_position_index, f"assets/{STYLE_FOLDER_NAME}/fonts")

    # === WATERMARK ===
    print(f"Pasting watermark")
    if not skip_watermark:
        img = watermark.paste_watermark(img)

    print("Done! Returning the image")
    # img.show()
    return img
