# finger_control.py

import cv2
import mediapipe as mp
import serial
import time

# Arduino seri portunu ayarla
ser = serial.Serial('COM3', 9600)  # Windows: COMx, Linux/Mac: /dev/ttyUSBx
time.sleep(2)  # Arduino'nun baþlatýlmasý için zaman taný

# MediaPipe eller
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

# Kamera baþlat
cap = cv2.VideoCapture(0)
frame_width = 640  # Giriþ videosunun geniþliði (kamera çözünürlüðü)

while True:
    success, img = cap.read()
    if not success:
        break

    img = cv2.flip(img, 1)  # Ayna görüntüsü
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    results = hands.process(img_rgb)

    if results.multi_hand_landmarks:
        handLms = results.multi_hand_landmarks[0]

        # Ýþaret parmaðý ucu (landmark 8)
        x = int(handLms.landmark[8].x * frame_width)
        cv2.circle(img, (x, 200), 15, (255, 0, 255), cv2.FILLED)

        # Açýyý hesapla (0-180 derece arasý)
        angle = int((x / frame_width) * 180)
        angle = max(0, min(180, angle))

        cv2.putText(img, f"Aci: {angle}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

        # Arduino'ya gönder
        try:
            ser.write(f"{angle}\n".encode())
        except:
            print("Veri gönderilemedi")

        # El çizimi
        mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)

    cv2.imshow("Finger Tracking", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
ser.close()
cv2.destroyAllWindows()
