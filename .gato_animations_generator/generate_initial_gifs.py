import math
import os
import sys
from io import BytesIO

import numpy as np
import requests
from PIL import Image, ImageDraw, ImageFont, ImageSequence

sys.path.append('gato')
from gatos import *

DIR = os.path.dirname(__file__)
os.chdir(DIR)

# COLOR : #F3F3F3

character_per_path: dict[str, list[str]] = {
    "hunt": ["seele", "swede", "dan heng", "sushang", "topaz"],
    "destruction": ["blade", "clara", "il", "xueyi", "jingliu"],
    "erudition": ["qingque", "cyxo", "herta", "himeko", "argenti"],
    "preservation": ["march 7th", "mak", "fuxuan"],
    "abundance": ["rei", "luocha", "huohuo"],
    "nihility": ["guinaifen", "kafka", "black swan", "acheron", "welt", "maple"],
    "harmony": ["emi lo", "lny", "sparkle", "tingyun", "asta", "yukong"],
    "item": ["example", "normal"]
}
path_for_character: dict[str, str] = {char: path for path, chars in character_per_path.items() for char in chars}

w, h = 1640, 924
target_item_size = 640
font = ImageFont.truetype("calibri.ttf", 36)
bigfont = ImageFont.truetype("calibri.ttf", 64)
total_frames = 37

# for itm in ALL_ITEMS:
for itm in [KafkaGato, GuinaifenGato, FuxuanGato, BladeGato, MedkitConsumable]:
    dest = "gifs/" + itm.ANIMATIONS
    if os.path.exists(dest):
        print("Folder", dest, "for", itm.DISPLAY_NAME, "already existed")
        continue
    os.mkdir(dest)
    frames: list[Image.Image] = []


    r = requests.get(itm.IMAGE)
    item_image = Image.open(BytesIO(r.content)).convert("RGBA")


    background_frames = []
    bg = Image.open(f"gifs/gato_bg{itm.RARITY}.gif")
    for frame in ImageSequence.Iterator(bg):
        background_frames.append(frame.resize((w, h)))
    background_frames = background_frames[3:total_frames+3]


    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if "Gato" in itm.__name__:
        nme: list[str] = list(itm.__name__.replace("Gato", ""))
        i = 1
        while i < len(nme):
            if nme[i-1] != " " and (nme[i].isupper() or nme[i].isnumeric()) and nme[i-1].islower():
                nme.insert(i, " ")
            i += 1
        type = "".join(nme)
        icon = path_for_character[type.lower()] + ".png"
    else:
        type = "Item"
        icon = "item.png"

    overdraw = ImageDraw.Draw(overlay, mode="RGBA")
    overdraw.rectangle((202, 374, 410, 418), (243, 243, 243, 255))

    overdraw.text((212, 378), type, (0, 0, 0, 255), font)

    infobg = Image.open("images/infobg.png")
    overlay.paste(infobg, (80, 432), infobg)

    icon = Image.open(f"images/{icon}").resize((85, 85))
    overlay.paste(icon, (104, 448), icon)

    overdraw.text((202, 438), itm.DISPLAY_NAME, (255, 255, 255, 255), bigfont)

    star = Image.open("images/star.png").resize((45, 45))
    for i in range(itm.RARITY):
        overlay.paste(star, (202 + i*46, 498), star)

    for t in range(total_frames):
        frame = Image.new("RGB", (w, h), (0, 0, 0))


        frame.paste(background_frames[t])


        if t < 5:
            item_opacity = t*20 / 100
        else:
            item_opacity = 1

        pix = np.array(item_image)
        pix[:,:,-1] = (pix[:,:,-1] * item_opacity).astype(np.int32)
        item_frame = Image.fromarray(pix)

        iw, ih = item_frame.size
        target_item_width = int(target_item_size / max(iw, ih) * iw)
        target_item_height = int(target_item_size / max(iw, ih) * ih)

        if t < 14:
            item_width = int((2*math.cos(t/math.pi*5/14) + 1) * target_item_width)
            item_height = int((2*math.cos(t/math.pi*5/14) + 1) * target_item_height)
        else:
            item_width = target_item_width
            item_height = target_item_height
        item_frame = item_frame.resize((item_width, item_height))

        x = int(w / 2 - item_width / 2)
        y = int(h / 2 - item_height / 2)
        frame.paste(item_frame, (x, y), item_frame)


        if t < 5:
            info_opacity = 0
        elif t > 15:
            info_opacity = 1
        else:
            info_opacity = 1/10*(t-5)

        pix = np.array(overlay)
        pix[:,:,-1] = (pix[:,:,-1] * info_opacity).astype(np.int32)
        info_frame = Image.fromarray(pix)

        if t < 5:
            d = 180
        elif t > 20:
            d = 0
        else:
            d = int(180/27*abs((t/5-4)**3))

        frame.paste(info_frame, (d, 0), info_frame)


        frames.append(frame)

    frames[0].save(dest + "/solo.gif", save_all=True, append_images=frames[1:], optimize=False, duration=33, loop=1)
    print("Saved", dest + "/solo.gif")
