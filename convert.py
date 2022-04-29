from PIL import Image, ImageOps
import os
import glob
import cv2
import numpy as np

PLAYER_COLOUR = (0, 0, 255)
AOE_FOLDER = r"D:\Games\SteamLibrary\steamapps\common\AoE2DE\widgetui\textures\ingame\units"

CIVS = {
    35: "Byzantines",
    36: "Chinese",
    37: "Saracens",
    38: "Vikings",
    39: "Turks",
    41: "Britons",
    42: "Mongols",
    43: "Persians",
    44: "Japanese",
    45: "Teutons",
    46: "Franks",
    47: "Celts",
    50: "Goths",
    93: "Indians",
    97: "Incas",
    99: "Magyars",
    105: "Huns",
    106: "Spanish",
    108: "Mayans",
    110: "Aztecs",
    114: "Slavs",
    117: "Koreans",
    133: "Italians",
    190: "Portuguese",
    191: "Berbers",
    195: "Ethiopians",
    197: "Malians",
    230: "Burmese",
    231: "Khmer",
    232: "Vietnamese",
    233: "Malay",
    250: "Bulgarians",
    251: "Tatars",
    252: "Cumans",
    253: "Lithuanians",
    355: "Burgundians",
    356: "Sicilians",
    369: "Poles",
    370: "Bohemians",
    385: "Hindustanis",
    386: "Dravidians",
    388: "Bengalis",
    390: "Gurjaras"
}


def scale(v):
    return (
        int(PLAYER_COLOUR[0] * (v[0] / 255)),
        int(PLAYER_COLOUR[1] * (v[1] / 255)),
        int(PLAYER_COLOUR[2] * (v[2] / 255)),
        255)


def is_empty(v):
    return v[0] == 0 and v[1] == 0 and v[2] == 0


def get_file_path(p, folder=None):
    texture_id = int(os.path.basename(p)[0:3])
    civ = CIVS.get(texture_id, texture_id)
    return os.path.join(folder, os.path.basename(f"{civ}.png"))


def main():
    pictures = glob.glob(os.path.join(AOE_FOLDER, "*.*"))

    for p in pictures:
        texture_id = int(os.path.basename(p)[0:3])
        if texture_id in CIVS:
            with Image.open(p) as im:
                r, g, b, a = im.split()

                rgb = Image.merge("RGB", (r, g, b))

                img = np.array(rgb)

                thresh1 = cv2.inRange(img, (14, 0, 0), (255, 255, 255))
                thresh2 = cv2.inRange(img, (0, 1, 0), (255, 255, 255))
                thresh3 = cv2.inRange(img, (0, 0, 1), (255, 255, 255))
                thresh = cv2.bitwise_and(thresh1, thresh2, thresh3)

                # apply morphology
                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
                thresh = cv2.morphologyEx(thresh, cv2.MORPH_DILATE, kernel)

                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (8, 8))
                thresh = cv2.morphologyEx(thresh, cv2.MORPH_ERODE, kernel)

                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (12, 12))
                thresh = cv2.morphologyEx(thresh, cv2.MORPH_DILATE, kernel)

                alpha = Image.fromarray(thresh)
                alpha.save(get_file_path(p, "generated_alpha"))

                rgb.putalpha(255)
                overlay = Image.new("RGBA", im.size, (255, 255, 255, 0))

                color_mask = Image.new("L", im.size, 0)
                color_mask.putalpha(ImageOps.invert(a))
                color_mask.save(get_file_path(p, "generated_masks"))

                w, h = im.size
                for x in range(w):
                    for y in range(h):
                        pixel = rgb.getpixel((x, y))
                        overlay.putpixel((x, y), scale(pixel))

                rgb.putalpha(alpha)
                rgb.save(get_file_path(p, "generated_base"))

                composite = Image.composite(rgb, overlay, a)
                composite.putalpha(alpha)
                composite.save(get_file_path(p, "generated_composite"))


if __name__ == '__main__':
    main()
