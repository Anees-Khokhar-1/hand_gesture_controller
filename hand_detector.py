"""
hand_detector.py
Handles MediaPipe hand detection and landmark extraction.
"""

import cv2
import mediapipe as mp
import math

class HandDetector:
    def __init__(self, max_hands=1, detection_conf=0.7, track_conf=0.7):
        self.max_hands = max_hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=self.max_hands,
            min_detection_confidence=detection_conf,
            min_tracking_confidence=track_conf
        )
        self.mp_draw = mp.solutions.drawing_utils

    def find_hands(self, img, draw=True):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.hands.process(img_rgb)

        h, w, _ = img.shape
        all_hands = []

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                lm_list = []
                x_list = []
                y_list = []

                for idx, lm in enumerate(hand_landmarks.landmark):
                    px, py = int(lm.x * w), int(lm.y * h)
                    lm_list.append((idx, px, py))
                    x_list.append(px)
                    y_list.append(py)

                bbox = (
                    min(x_list), min(y_list),
                    max(x_list) - min(x_list),
                    max(y_list) - min(y_list)
                )

                all_hands.append({'lm': lm_list, 'bbox': bbox})

                if draw:
                    self.mp_draw.draw_landmarks(
                        img,
                        hand_landmarks,
                        self.mp_hands.HAND_CONNECTIONS
                    )

        return img, all_hands

    @staticmethod
    def distance(p1, p2):
        _, x1, y1 = p1
        _, x2, y2 = p2
        return math.hypot(x2 - x1, y2 - y1)
