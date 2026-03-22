import cv2
import numpy as np
import json
import os
from tkinter import *
from tkinter import filedialog

def export_preset(l_h, l_s, l_v, u_h, u_s, u_v):
    file_path = filedialog.asksaveasfilename(
        initialdir=os.getcwd(),
        defaultextension='.json',
        filetypes=[('JSON Files', '*.json')]
    )

    if file_path:
        data = {
            'lower': [l_h, l_s, l_v],
            'upper': [u_h, u_s, u_v]
        }
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
        print(f'Exported to {file_path}')

def nothing(x):
    pass

# setup tkinter (save preset)
root = Tk()
root.title('Control Panel')
root.geometry('200x100')
btn_export = Button(root, text='Export JSON', 
                    command=lambda:export_preset(
                        cv2.getTrackbarPos("L - H", "Trackbars"),
                        cv2.getTrackbarPos("L - S", "Trackbars"),
                        cv2.getTrackbarPos("L - V", "Trackbars"),
                        cv2.getTrackbarPos("U - H", "Trackbars"),
                        cv2.getTrackbarPos("U - S", "Trackbars"),
                        cv2.getTrackbarPos("U - V", "Trackbars")
                    ),
                    bg='green', fg='white', font=('Arial', 10, 'bold'))
btn_export.pack(expand=True, fill=BOTH, padx=10, pady=10)

cap = cv2.VideoCapture(0)
cv2.namedWindow("Trackbars")

# H = Hue, S = Saturation, V = Value
# Lower - Upper => Threshold supaya tangan kedetect
cv2.createTrackbar("L - H", "Trackbars", 0, 179, nothing)
cv2.createTrackbar("L - S", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("L - V", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("U - H", "Trackbars", 179, 179, nothing)
cv2.createTrackbar("U - S", "Trackbars", 255, 255, nothing)
cv2.createTrackbar("U - V", "Trackbars", 255, 255, nothing)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # mirroring frame
    frame = cv2.flip(frame, 1)

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV) # BGR -> HSV

    l_h = cv2.getTrackbarPos("L - H", "Trackbars")
    l_s = cv2.getTrackbarPos("L - S", "Trackbars")
    l_v = cv2.getTrackbarPos("L - V", "Trackbars")
    u_h = cv2.getTrackbarPos("U - H", "Trackbars")
    u_s = cv2.getTrackbarPos("U - S", "Trackbars")
    u_v = cv2.getTrackbarPos("U - V", "Trackbars")

    lower_skin = np.array([l_h, l_s, l_v])
    upper_skin = np.array([u_h, u_s, u_v])

    mask = cv2.inRange(hsv, lower_skin, upper_skin)

    cv2.putText(frame, "Press 's' to Export Preset", (20, 450), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    cv2.imshow("Camera", frame)
    cv2.imshow("Mask Kalibrasi Camera", mask)

    root.update_idletasks()
    root.update()

    key = cv2.waitKey(1) & 0xFF

    # if key == ord('s'):
    #     export_preset(l_h, l_s, l_v, u_h, u_s, u_v)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
root.destroy()