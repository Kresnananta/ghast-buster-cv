import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import constant

MENU_ITEMS = [
    "Play Game",
    "Calibrate Camera",
    "Import Preset",
    "Quit Game",
]

def draw_pillow_text(frame, text, position, font_size, color, anchor="mm"):
    image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(constant.MENU_FONT_ASSET, font_size)

    draw.text(
        position,
        text,
        font=font,
        fill=color,
        anchor=anchor,
    )

    return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)


def draw_menu_button(frame, text, x, y, w, h, selected=False):
    fill = (180, 180, 180) if selected else (120, 120, 120)
    top_light = (235, 235, 235)
    bottom_shadow = (40, 40, 40)
    border = (15, 15, 15)

    cv2.rectangle(frame, (x, y), (x + w, y + h), border, -1)
    cv2.rectangle(frame, (x + 3, y + 3), (x + w - 3, y + h - 3), fill, -1)

    cv2.line(frame, (x + 3, y + 3), (x + w - 3, y + 3), top_light, 2)
    cv2.line(frame, (x + 3, y + 3), (x + 3, y + h - 3), top_light, 2)
    cv2.line(frame, (x + 3, y + h - 3), (x + w - 3, y + h - 3), bottom_shadow, 2)
    cv2.line(frame, (x + w - 3, y + 3), (x + w - 3, y + h - 3), bottom_shadow, 2)

    if selected:
        cv2.rectangle(frame, (x - 3, y - 3), (x + w + 3, y + h + 3), (255, 255, 255), 2)

    frame[:] = draw_pillow_text(
        frame,
        text,
        (x + w // 2, y + h // 2 + 2),
        22,
        (255, 255, 255),
    )


def draw_main_menu(background, selected_index):
    frame = background.copy()

    dark = np.zeros_like(frame)
    frame = cv2.addWeighted(frame, 0.65, dark, 0.35, 0)

    frame = draw_pillow_text(
        frame,
        "GHAST BUSTER CV",
        (constant.CAM_W // 2, 105),
        52,
        (235, 235, 235),
    )

    frame = draw_pillow_text(
        frame,
        "Final Project Edition!",
        (constant.CAM_W // 2 + 135, 145),
        20,
        (255, 255, 0),
    )

    button_w = 330
    button_h = 42
    button_x = (constant.CAM_W - button_w) // 2
    start_y = 190
    gap = 52

    for i, item in enumerate(MENU_ITEMS):
        button_y = start_y + i * gap
        draw_menu_button(
            frame,
            item,
            button_x,
            button_y,
            button_w,
            button_h,
            selected_index == i,
        )

    frame = draw_pillow_text(
        frame,
        "W/S or Arrow Keys to Select   Enter to Confirm",
        (constant.CAM_W // 2, constant.CAM_H - 28),
        16,
        (230, 230, 230),
    )

    return frame


def handle_menu_input(key, selected_index):
    if key in [ord('w'), ord('W'), 82]:
        selected_index = (selected_index - 1) % len(MENU_ITEMS)

    elif key in [ord('s'), ord('S'), 84]:
        selected_index = (selected_index + 1) % len(MENU_ITEMS)

    elif key in [13, 10]:
        return selected_index, MENU_ITEMS[selected_index]

    elif key == ord('q'):
        return selected_index, "Quit Game"

    return selected_index, None