"""
app.py
Main App — Real-Time Hand Gesture Controller
"""

import cv2
import time
import pyautogui

from hand_detector import HandDetector
from gesture_controller import GestureController


def main():
    print("🚀 Starting Hand Gesture Controller...")

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("❌ ERROR: Webcam not detected!")
        print("Tip: Close other apps using the camera (Zoom, Chrome, Teams, etc.)")
        return

    print("📷 Webcam initialized successfully!")

    cap.set(3, 1280)
    cap.set(4, 720)

    detector = HandDetector()
    screen_w, screen_h = pyautogui.size()
    controller = GestureController(screen_w, screen_h)

    mode = "volume"  
    last_click = 0

    print("✅ System Ready!")
    print("Controls:")
    print("   v = Volume Mode")
    print("   b = Brightness Mode")
    print("   m = Mouse Control Mode")
    print("   q = Quit\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ ERROR: Failed to read from webcam.")
            break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        frame, hands = detector.find_hands(frame)

        info = f"Mode: {mode}"

        if hands:
            hand = hands[0]
            lm = hand['lm']

            fingers = controller.fingers_up(lm)
            pinch, dist = controller.is_pinch(lm)

            # ---- Volume Mode ----
            if mode == "volume":
                if pinch:
                    controller.set_volume(dist)
                    info += f" | Volume Level"

            # ---- Brightness Mode ----
            elif mode == "brightness":
                if pinch:
                    controller.set_brightness(dist)
                    info += f" | Brightness Level"

            # ---- Mouse Mode ----
            elif mode == "mouse":
                index_finger = [p for p in lm if p[0] == 8][0]
                controller.move_cursor(index_finger, w, h)

                if pinch and time.time() - last_click > 0.4:
                    controller.click()
                    last_click = time.time()
                    info += " | Click"

        cv2.putText(frame, info, (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("Hand Gesture Control", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            break
        if key == ord('v'):
            mode = "volume"
        if key == ord('b'):
            mode = "brightness"
        if key == ord('m'):
            mode = "mouse"

    cap.release()
    cv2.destroyAllWindows()
    print("👋 Program closed.")


if __name__ == "__main__":
    main()
