import cv2
import numpy as np
import constant

def overlay_transparent(background, overlay, x, y):
    h, w = overlay.shape[:2]
    bg_h, bg_w = background.shape[:2]

    if x >= bg_w or y>= bg_h or x + w <= 0 or y + h <= 0:
        return background
    
    x1 = max(x, 0)
    y1 = max(y, 0)
    x2 = min(x + w, bg_w)
    y2 = min(y + h, bg_h)

    overlay_x1 = x1 - x
    overlay_y1 = y1 - y
    overlay_x2 = overlay_x1 + (x2 - x1)
    overlay_y2 = overlay_y1 + (y2 - y1)

    overlay_crop = overlay[overlay_y1:overlay_y2, overlay_x1:overlay_x2]

    if overlay_crop.shape[2] < 4:
        background[y1:y2, x1:x2] = overlay_crop
        return background
    
    alpha = overlay_crop[:, :, 3] / 255.0
    alpha = alpha[:, :, np.newaxis]

    foreground = overlay_crop[:, :, :3]
    background_crop = background[y1:y2, x1:x2]

    blended = (foreground * alpha) + (background_crop * (1 - alpha))
    background[y1:y2, x1:x2] = blended.astype(np.uint8)

    return background


def draw_pixel_heart(frame, x, y, filled=True):
    color = (0, 0, 255) if filled else (45, 45, 45)
    outline = (255, 255, 255)

    pattern = [
        "01100110",
        "11111111",
        "11111111",
        "11111111",
        "01111110",
        "00111100",
        "00011000",
    ]

    scale = 3

    for row, line in enumerate(pattern):
        for col, pixel in enumerate(line):
            if pixel == "1":
                x1 = x + col * scale
                y1 = y + row * scale
                cv2.rectangle(frame, (x1, y1), (x1 + scale, y1 + scale), color, -1)

    cv2.rectangle(frame, (x, y), (x + 8 * scale, y + 7 * scale), outline, 1)


def draw_hp(frame, hp):
    for i in range(constant.MAX_HP):
        heart_x = 20 + i * 32
        heart_y = 45
        draw_pixel_heart(frame, heart_x, heart_y, i < hp)


def draw_deflect_effects(frame, deflect_effects):
    for effect in deflect_effects[:]:
        life = effect["life"]
        max_life = effect["max_life"]

        intensity = int(255 * (life / max_life))
        spark_color = (0, min(255, intensity + 80), 255)

        for spark in effect["sparks"]:
            spark["x"] += spark["vx"]
            spark["y"] += spark["vy"]
            spark["vy"] += 0.35

            sx = int(spark["x"])
            sy = int(spark["y"])

            cv2.rectangle(frame, (sx - 2, sy - 2), (sx + 2, sy + 2), spark_color, -1)

        effect["life"] -= 1

        if effect["life"] <= 0:
            deflect_effects.remove(effect)


def draw_shield(frame, shield_img, cx, cy):
    shield_x = cx - constant.SHIELD_SIZE // 2
    shield_y = cy - constant.SHIELD_SIZE // 2
    overlay_transparent(frame, shield_img, shield_x, shield_y)


def draw_ghast(frame, ghast, ghast_idle_frames, ghast_shooting_img, frame_count, ghast_idle_index):
    if ghast["state"] == "idle":
        if frame_count % 4 == 0:
            ghast_idle_index = (ghast_idle_index + 1) % len(ghast_idle_frames)

        current_ghast_img = ghast_idle_frames[ghast_idle_index]
    else:
        current_ghast_img = ghast_shooting_img

    overlay_transparent(frame, current_ghast_img, int(ghast["x"]), ghast["y"])

    return ghast_idle_index


def draw_fireballs(frame, fireballs, fireball_img):
    for fireball in fireballs:
        fx = fireball["x"]
        fy = fireball["y"]

        fireball_x = int(fx) - constant.FIREBALL_SIZE // 2
        fireball_y = int(fy) - constant.FIREBALL_SIZE // 2
        overlay_transparent(frame, fireball_img, fireball_x, fireball_y)


def draw_game_over(frame):
    dim = frame.copy()
    cv2.rectangle(dim, (0, 0), (constant.CAM_W, constant.CAM_H), (0, 0, 0), -1)
    frame = cv2.addWeighted(frame, 0.45, dim, 0.55, 0)

    cv2.putText(frame, "GAME OVER", (145, 220),
                cv2.FONT_HERSHEY_SIMPLEX, 1.4, (0, 0, 255), 4)
    cv2.putText(frame, "Press R to Restart or Q to Quit", (95, 265),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
    
    return frame