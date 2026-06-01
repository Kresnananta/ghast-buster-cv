import cv2
import numpy as np

def detect_hand(frame, lower_skin, upper_skin):
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
    
    return mask, hand_detected, cx, cy, largest_contour