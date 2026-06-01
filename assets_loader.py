import cv2
import numpy as np
from PIL import Image, ImageSequence
import constant

def load_gif_frames(path, size):
    gif = Image.open(path)
    frames = []

    for frame in ImageSequence.Iterator(gif):
        frame = frame.convert("RGBA")
        frame = frame.resize(size, Image.Resampling.NEAREST)

        rgba = np.array(frame)
        bgra = cv2.cvtColor(rgba, cv2.COLOR_RGBA2BGRA)

        frames.append(bgra)

    if not frames:
        raise FileNotFoundError(f'GIF tidak bisa dibaca: {path}')

    return frames

def load_assets():
    shield_img = cv2.imread(constant.SHIELD_ASSET, cv2.IMREAD_UNCHANGED)
    fireball_img = cv2.imread(constant.FIREBALL_ASSET, cv2.IMREAD_UNCHANGED)
    ghast_shooting_img = cv2.imread(constant.GHAST_SHOOTING_ASSET, cv2.IMREAD_UNCHANGED)
    ghast_idle_frames = load_gif_frames(
        constant.GHAST_IDLE_ASSET,
        (constant.GHAST_W, constant.GHAST_H)
    )
    menu_background = cv2.imread(constant.MENU_BACKGROUND_ASSET)

    if shield_img is None:
        raise FileNotFoundError(f'Asset tidak ditemukan: {constant.SHIELD_ASSET}')

    if fireball_img is None:
        raise FileNotFoundError(f'Asset tidak ditemukan: {constant.FIREBALL_ASSET}')

    if ghast_shooting_img is None:
        raise FileNotFoundError(f'Asset tidak ditemukan: {constant.GHAST_SHOOTING_ASSET}')
    
    if menu_background is None:
        raise FileNotFoundError(f'Asset tidak ditemukan: {constant.MENU_BACKGROUND_ASSET}')

    shield_img = cv2.resize(
        shield_img,
        (constant.SHIELD_SIZE, constant.SHIELD_SIZE),
        interpolation=cv2.INTER_NEAREST
    )

    fireball_img = cv2.resize(
        fireball_img,
        (constant.FIREBALL_SIZE, constant.FIREBALL_SIZE),
        interpolation=cv2.INTER_NEAREST
    )

    ghast_shooting_img = cv2.resize(
        ghast_shooting_img,
        (constant.GHAST_W, constant.GHAST_H),
        interpolation=cv2.INTER_NEAREST
    )

    menu_background = cv2.resize(
        menu_background,
        (constant.CAM_W, constant.CAM_H),
        interpolation=cv2.INTER_AREA
    )

    return {
        "shield": shield_img,
        "fireball": fireball_img,
        "ghast_idle_frames": ghast_idle_frames,
        "ghast_shooting": ghast_shooting_img,
        "menu_background": menu_background,
    }