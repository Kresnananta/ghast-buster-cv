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

cap = cv2.VideoCapture(0)

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

                cv2.circle(frame, (cx, cy), constant.SHIELD_RAD, (0, 255, 255), 3)
                cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
                
                cv2.drawContours(frame, [largest_contour], -1, (0, 255, 0), 2) # gambar area tangan

    if random.randint(1, 20) == 1:
        random_x = random.randint(constant.ENEMY_RAD, 640 - constant.ENEMY_RAD)
        enemies.append([random_x, 0])

    for enemy in enemies[:]:
        ex, ey = enemy[0], enemy[1]
        enemy[1] += constant.ENEMY_SPEED

        cv2.circle(frame, (ex, int(enemy[1])), constant.ENEMY_RAD, (0, 0, 255), -1)

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