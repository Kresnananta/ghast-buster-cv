import cv2
import numpy as np
from menu import draw_pillow_text, draw_menu_button

DEATH_MENU_ITEMS = [
    "Retry",
    "Main Menu",
]

def draw_death_screen(background_frame,score, selected_index):
    frame = background_frame.copy()

    red_overlay = np.zeros_like(frame)

    for y in range(frame.shape[0]):
        ratio = y / frame.shape[0]
        red = int(65 + ratio * 80)
        red_overlay[y, :] = (25, 25, red)

    frame = cv2.addWeighted(frame, 0.35, red_overlay, 0.65, 0)

    frame = draw_pillow_text(
        frame,
        "You Died!",
        (320, 140),
        42,
        (230, 230, 230),
    )

    frame = draw_pillow_text(
        frame,
        "Steve was killed",
        (320, 185),
        22,
        (230, 230, 230),
    )

    frame = draw_pillow_text(
        frame,
        f"Score: {score}",
        (320, 218),
        22,
        (255, 255, 0),
    )

    button_w = 360
    button_h = 42
    button_x = (640 - button_w) // 2
    start_y = 285
    gap = 55

    for i, item in enumerate(DEATH_MENU_ITEMS):
        draw_menu_button(
            frame,
            item,
            button_x,
            start_y + i * gap,
            button_w,
            button_h,
            selected_index == i,
        )

    return frame


def handle_death_input(key, selected_index):
    if key in [ord('w'), ord('W'), 82]:
        selected_index = (selected_index - 1) % len(DEATH_MENU_ITEMS)

    elif key in [ord('s'), ord('S'), 84]:
        selected_index = (selected_index + 1) % len(DEATH_MENU_ITEMS)

    elif key in [13, 10]:
        return selected_index, DEATH_MENU_ITEMS[selected_index]

    elif key == ord('r'):
        return selected_index, "Retry"

    elif key == ord('m'):
        return selected_index, "Main Menu"

    return selected_index, None