from PIL import Image, ImageOps, ImageDraw, ImageFilter
import random as rnd

from generator import sector_manager


def paste_user_image(img: Image, user_img: Image, position_index, is_png=False) -> Image:
    # Resize it
    wth_ratio = user_img.width / user_img.height
    htw_ratio = user_img.height / user_img.width

    new_height = round(img.height / 2)
    new_width = round(new_height * wth_ratio)

    if new_width > img.width / 3:
        new_width = round(img.width / 3)
        new_height = round(new_width * htw_ratio)

    new_size = (new_width, new_height)

    user_img = user_img.resize(new_size)

    # Mirror it (or not, what do I care)
    if rnd.randint(0, 1) == 1:
        user_img = ImageOps.mirror(user_img)

    # Rotate a little
    rotation = rnd.randint(-12, 12)
    user_img = user_img.rotate(rotation, expand=True)

    # Get position
    position = sector_manager.get_sector_coords(position_index,
                                                img.width, img.height)

    position = (position[0] - round(user_img.width / 2), position[1] - round(user_img.height / 2))

    if not is_png:
        mask = Image.new("L", user_img.size, 0)
        draw = ImageDraw.Draw(mask)
        padding_w = user_img.width / 8
        padding_h = user_img.height / 8
        draw.ellipse((padding_w, padding_h, user_img.width - padding_w, user_img.height - padding_h), fill=255)
        mask_blur = mask.filter(ImageFilter.GaussianBlur(20))

        print(f"Pasting user image at index {position_index}, position {position}")
        # Paste image over background
        img.paste(user_img,
                  position,
                  mask_blur)
    else:
        img.paste(user_img,
                  position,
                  user_img)

    return img
