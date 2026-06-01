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

cap = cv2.VideoCapture(0)

# load assets
shield_img = cv2.imread(constant.SHIELD_ASSET, cv2.IMREAD_UNCHANGED)
fireball_img = cv2.imread(constant.FIREBALL_ASSET, cv2.IMREAD_UNCHANGED)

if shield_img is None or fireball_img is None:
    raise FileNotFoundError('Asset shileld.png atau fireball.png tidak ditemukan di folder assets')

shield_img = cv2.resize(shield_img, (constant.SHIELD_SIZE, constant.SHIELD_SIZE))
fireball_img = cv2.resize(fireball_img, (constant.FIREBALL_SIZE, constant.FIREBALL_SIZE))

# default value
lower_skin = constant.DEFAULT_LOWER_SKIN
upper_skin = constant.DEFAULT_UPPER_SKIN

enemies = []

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

    if random.randint(1, 20) == 1:
        random_x = random.randint(constant.ENEMY_RAD, 640 - constant.ENEMY_RAD)
        enemies.append([random_x, 0])

    for enemy in enemies[:]:
        ex, ey = enemy[0], enemy[1]
        enemy[1] += constant.ENEMY_SPEED

        # draw fireball
        fireball_x = ex - constant.FIREBALL_SIZE // 2
        fireball_y = int(enemy[1]) - constant.FIREBALL_SIZE // 2
        overlay_transparent(frame, fireball_img, fireball_x, fireball_y)

        # colision check
        if hand_detected:
            # euclidean distance
            distance = math.sqrt(pow((cx - ex), 2) + pow((cy - enemy[1]), 2))

            if distance < (constant.SHIELD_RAD + constant.ENEMY_RAD):
                enemies.remove(enemy)
                # efek
                cv2.circle(frame, (ex, int(enemy[1])), constant.ENEMY_RAD + 20, (255, 255, 255), 2)
                continue
            
        # kalo enemy lolos
        if enemy[1] > 480:
            enemies.remove(enemy)
            # harusnya hitpoint berkurang nanti

    cv2.putText(frame, "Press 'i' to Import Preset", (20, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    cv2.imshow("Shield Defense", frame)
    cv2.imshow("Clean Mask", mask)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('i'):
        new_lower, new_upper = import_preset()
        if new_lower is not None:
            lower_skin = new_lower
            upper_skin = new_upper
            print('Preset berhasil di import')

    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()