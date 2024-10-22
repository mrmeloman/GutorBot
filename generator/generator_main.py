from generator.generator_regular import generate_regular


# TODO list:
# 1. I can build an "emptiness" heatmap by difference between background image and final image
# 1.2 I will obviously need to use sectors for the heatmap, no point in doing it pixel-perfect, will be too precise to use

# 2. I can build a heatmap for every step so I place object/animal/flowers on a random empty space, so they won't interlap
# 2.2 This will make placement more random and less interlapping (well, depending on the error that I can control)
# 2.3 Maybe I can still place objects in the sectors, just nudge them towards more empty areas within sector + error

# 3. Gradient text
# 4. Text shadows
# 5. 3d bubbly text
# 6. Distorted text like waves or so

# Multithreading
# User pic database?
# Styles? Wolves?
# Normal text wrapping

async def generate_postcard(query: str, usr_image=None, style="regular", is_png=False):
    print(f"Style selected: {style}")

    if style == "regular":
        img = await generate_regular(query, usr_image, is_png=is_png)
    else:
        img = None

    return img
