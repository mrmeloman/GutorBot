from PIL import Image
import random, os


def paste_overlay(img: Image, assets_path: str) -> Image:
    v_path = random.choice(os.listdir(assets_path))
    v_path = f"{assets_path}/{v_path}"
    v_img = Image.open(v_path).convert("RGBA")

    if v_img.size != img.size:
        v_img = v_img.resize(img.size)

    img.paste(v_img,
              (0, 0),
              v_img)

    return img
