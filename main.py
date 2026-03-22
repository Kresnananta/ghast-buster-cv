import cv2
import numpy as np
import json
import os
from tkinter import filedialog, Tk


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
lower_skin = np.array([0, 23, 141])
upper_skin = np.array([89, 255, 255])

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

                cv2.circle(frame, (cx, cy), 50, (0, 255, 255), 3)
                cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
                
                cv2.drawContours(frame, [largest_contour], -1, (0, 255, 0), 2)

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