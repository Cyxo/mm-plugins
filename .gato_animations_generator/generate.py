import json
import os

import cv2
import imageio.v3 as iio
import numpy as np
import requests
from dotenv import load_dotenv

DIR = os.path.dirname(__file__)
os.chdir(DIR)

load_dotenv()


def discord_send_file(file_name: str) -> str:
    files = {
        'payload_json': (None, '{"username": "test", "content": "hello"}'),
        'file1': open(file_name, 'rb')
    }

    response = requests.post(os.getenv('WEBHOOK_URL', ''), files=files)

    return response.json()["attachments"][0]["proxy_url"]


def make_static(size, gif):
    p = os.path.join("gifs", gif)
    frame = cv2.resize(iio.imread(p)[-1], size[::-1])
    iio.imwrite(os.path.join(os.path.dirname(p), "static.png"), frame)


def combine_gifs(size, *gifs: str, optimize=True):
    paths = [os.path.join("gifs", gif) for gif in gifs]
    frames = [iio.imread(path) for path in paths]

    for g, gif in enumerate(frames):
        if gif.shape[1:3] != size:
            res = np.zeros((gif.shape[0], size[0], size[1], gif.shape[3]), dtype=np.uint8)
            for i in range(gif.shape[0]):
                res[i,:,:,:] = cv2.resize(gif[i], size[::-1])
            frames[g] = res

    frames = np.vstack(frames)
    iio.imwrite("tempt.gif", frames, duration=33)
    if optimize:
        os.system(f"{os.getenv('GIFSICLE', './gifsicle')} --lossy=30 -o temp.gif tempt.gif")
        os.remove("tempt.gif")
    else:
        if os.path.exists("temp.gif"):
            os.remove("temp.gif")
        os.rename("tempt.gif", "temp.gif")

    return frames.shape[0] * 33 / 1000


res = {}
if os.path.exists("animations.json"):
    with open("animations.json", "r") as f:
        res = json.load(f)

for d in os.listdir("gifs"):
    if not os.path.isdir(os.path.join("gifs", d)):
        continue

    anim = {}

    for train in ["train3.gif", "train4.gif", "train5.gif", "train6.gif"]:
        print(d, train)
        duration = combine_gifs((240, 426), train, "transi.gif", os.path.join(d, "solo.gif"))
        url = discord_send_file("temp.gif")
        anim[train.split(".")[0]] = {
            "url": url,
            "duration": duration
        }

    print(d, "static")
    make_static((240, 426), os.path.join(d, "solo.gif"))
    url = discord_send_file(os.path.join("gifs", d, "static.png"))
    anim["static"] = {
        "url": url,
        "duration": 0
    }

    print(d, "solo")
    duration = combine_gifs((240, 426), os.path.join(d, "solo.gif"), optimize=False)
    url = discord_send_file("temp.gif")
    anim["solo"] = {
        "url": url,
        "duration": duration
    }

    res[d] = anim

    with open("animations.json", "w+") as f:
        json.dump(res, f)
