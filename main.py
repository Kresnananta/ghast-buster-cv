import cv2
import numpy as np
import json
import os
from tkinter import filedialog, Tk
import random
import math
import constant


def import_preset():
    root = Tk()
    root.withdraw()
    root.attributes('-topmost', True)

    file_path = filedialog.askopenfilename(
        initialdir=os.path.join(os.getcwd(), 'preset'),
        title="Pilih preset kamera",
        filetypes=[('JSON Files', '*.json')]
    )
    root.destroy()

    if file_path:
        with open(file_path, 'r') as f:
            data = json.load(f)
            return np.array(data['lower']), np.array(data['upper'])
    
    # kalau di cancel
    return None, None

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

def load_gif_frames(path, size):
    cap = cv2.VideoCapture(path)
    frames = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.resize(frame, size)

        # GIF dari OpenCV biasanya BGR tanpa alpha.
        # Background hitam dibuat transparan.
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        alpha = np.where(gray > 10, 255, 0).astype(np.uint8)

        frame_bgra = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)
        frame_bgra[:, :, 3] = alpha

        frames.append(frame_bgra)

    cap.release()

    if not frames:
        raise FileNotFoundError(f'GIF tidak bisa dibaca: {path}')

    return frames

def spawn_deflect_effect(x, y):
    sparks = []

    for _ in range(constant.DEFLECT_SPARK_COUNT):
        angle = random.uniform(-math.pi, 0)
        speed = random.uniform(3, constant.DEFLECT_SPARK_SPEED)

        sparks.append({
            "x": x,
            "y": y,
            "vx": math.cos(angle) * speed,
            "vy": math.sin(angle) * speed,
        })

    deflect_effects.append({
        "x": x,
        "y": y,
        "life": constant.DEFLECT_EFFECT_LIFE,
        "max_life": constant.DEFLECT_EFFECT_LIFE,
        "sparks": sparks,
    })

def draw_deflect_effects(frame):
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

def create_ghast():
    return {
        "x": (constant.CAM_W - constant.GHAST_W) // 2,
        "y": constant.GHAST_Y,
        "vx": constant.GHAST_SPEED,
        "cooldown": constant.FIREBALL_COOLDOWN,
        "state": "idle",
        "shoot_timer": 0,
        "burst_left": 0,
        "burst_timer": 0,
    }

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

cap = cv2.VideoCapture(0)

# load assets
shield_img = cv2.imread(constant.SHIELD_ASSET, cv2.IMREAD_UNCHANGED)
fireball_img = cv2.imread(constant.FIREBALL_ASSET, cv2.IMREAD_UNCHANGED)
ghast_idle_frames = load_gif_frames(
    constant.GHAST_IDLE_ASSET,
    (constant.GHAST_W, constant.GHAST_H)
)
ghast_shooting_img = cv2.imread(constant.GHAST_SHOOTING_ASSET, cv2.IMREAD_UNCHANGED)

if shield_img is None or fireball_img is None or ghast_shooting_img is None:
    raise FileNotFoundError('Asset shileld.png, fireball.png, atau ghast_shooting.png tidak ditemukan di folder assets')

shield_img = cv2.resize(shield_img, (constant.SHIELD_SIZE, constant.SHIELD_SIZE))
fireball_img = cv2.resize(fireball_img, (constant.FIREBALL_SIZE, constant.FIREBALL_SIZE))
ghast_shooting_img = cv2.resize(
    ghast_shooting_img,
    (constant.GHAST_W, constant.GHAST_H)
)

# default value
lower_skin = constant.DEFAULT_LOWER_SKIN
upper_skin = constant.DEFAULT_UPPER_SKIN

ghast = create_ghast()
fireballs = []
deflect_effects = []

hp = constant.MAX_HP
game_over = False

frame_count = 0
ghast_idle_index = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, lower_skin, upper_skin) # threshold 
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.erode(mask, kernel, iterations=1) # mengikis noise kecil
    mask = cv2.dilate(mask, kernel, iterations=2) # menebalkan tangan kembali

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    cx, cy = 0, 0
    hand_detected = False

    if contours:
        # ambil contour yg paling luas (meminimalisir wajah terdetek)
        largest_contour = max(contours, key=cv2.contourArea)
        if cv2.contourArea(largest_contour) > 1000:
            # cari titik tengah
            M = cv2.moments(largest_contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                # m00 = total luas area putih; m10 & m01 = jumlah posisi pixel
                hand_detected = True

                # draw shield
                shield_x = cx - constant.SHIELD_SIZE // 2
                shield_y = cy - constant.SHIELD_SIZE // 2
                overlay_transparent(frame, shield_img, shield_x, shield_y)
                
                cv2.drawContours(frame, [largest_contour], -1, (0, 255, 0), 2) # gambar area tangan

    # ghast movemenent + shooting
    frame_count += 1

    if not game_over:
        if ghast["state"] == "idle":
            ghast["x"] += ghast["vx"]

            if ghast["x"] <= 0 or ghast["x"] + constant.GHAST_W >= constant.CAM_W:
                ghast["vx"] *= -1
                ghast["x"] = max(0, min(ghast["x"], constant.CAM_W - constant.GHAST_W))

            ghast["cooldown"] -= 1

            if ghast["cooldown"] <= 0:
                ghast["state"] = "shooting"
                ghast["shoot_timer"] = constant.GHAST_SHOOT_DURATION
                ghast["burst_left"] = constant.GHAST_BURST_COUNT
                ghast["burst_timer"] = constant.GHAST_SHOOT_START_DELAY

        elif ghast["state"] == "shooting":
            ghast["shoot_timer"] -= 1
            ghast["burst_timer"] -= 1

            if ghast["burst_left"] > 0 and ghast["burst_timer"] <= 0 and len(fireballs) < constant.MAX_FIREBALLS:
                mouth_x = int(ghast["x"]) + constant.GHAST_MOUTH_OFFSET_X
                mouth_y = ghast["y"] + constant.GHAST_MOUTH_OFFSET_Y

                spread_index = ghast["burst_left"] - 1
                spread_values = [-constant.GHAST_FIREBALL_SPREAD_X, 0, constant.GHAST_FIREBALL_SPREAD_X]
                vx = spread_values[spread_index % len(spread_values)]

                fireballs.append({
                    "x": mouth_x,
                    "y": mouth_y,
                    "vx": vx,
                    "vy": constant.ENEMY_SPEED,
                })

                ghast["burst_left"] -= 1
                ghast["burst_timer"] = constant.GHAST_BURST_INTERVAL

            if ghast["shoot_timer"] <= 0:
                ghast["state"] = "idle"
                ghast["cooldown"] = constant.FIREBALL_COOLDOWN

    # render ghast
    if ghast["state"] == "idle":
        if frame_count % 4 == 0:
            ghast_idle_index = (ghast_idle_index + 1) % len(ghast_idle_frames)

        current_ghast_img = ghast_idle_frames[ghast_idle_index]
    else:
        current_ghast_img = ghast_shooting_img

    overlay_transparent(frame, current_ghast_img, int(ghast["x"]), ghast["y"])


    for fireball in fireballs[:]:
        if not game_over:
            fireball["x"] += fireball["vx"]
            fireball["y"] += fireball["vy"]

        fx = fireball["x"]
        fy = fireball["y"]

        fireball_x = int(fx) - constant.FIREBALL_SIZE // 2
        fireball_y = int(fy) - constant.FIREBALL_SIZE // 2
        overlay_transparent(frame, fireball_img, fireball_x, fireball_y)

        if hand_detected and not game_over:
            distance = math.sqrt(pow((cx - fx), 2) + pow((cy - fy), 2))

            if distance < (constant.SHIELD_RAD + constant.ENEMY_RAD):
                fireballs.remove(fireball)
                spawn_deflect_effect(int(fx), int(fy))
                continue

        if fy > constant.CAM_H or fx < 0 or fx > constant.CAM_W:
            fireballs.remove(fireball)
            hp -= 1

            if hp <= 0:
                hp = 0
                game_over = True

    draw_deflect_effects(frame)
    draw_hp(frame, hp)

    if game_over:
        dim = frame.copy()
        cv2.rectangle(dim, (0, 0), (constant.CAM_W, constant.CAM_H), (0, 0, 0), -1)
        frame = cv2.addWeighted(frame, 0.45, dim, 0.55, 0)

        cv2.putText(frame, "GAME OVER", (145, 220),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.4, (0, 0, 255), 4)
        cv2.putText(frame, "Press R to Restart or Q to Quit", (95, 265),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)

    cv2.putText(frame, "Press 'i' to Import Preset", (20, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    cv2.imshow("Shield Defense", frame)
    cv2.imshow("Clean Mask", mask)

    key = cv2.waitKey(1) & 0xFF

    # import preset
    if key == ord('i'):
        new_lower, new_upper = import_preset()
        if new_lower is not None:
            lower_skin = new_lower
            upper_skin = new_upper
            print('Preset berhasil di import')
    
    # restart game
    elif key == ord('r'):
        ghast = create_ghast()
        fireballs.clear()
        deflect_effects.clear()
        hp = constant.MAX_HP
        game_over = False
        frame_count = 0
        ghast_idle_index = 0

    # quit game
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()