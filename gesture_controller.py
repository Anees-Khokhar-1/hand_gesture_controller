"""
gesture_controller.py
Handles gesture interpretation and controls volume, brightness, mouse actions.
"""

import numpy as np
import pyautogui
import screen_brightness_control as sbc
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
import time

from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


def get_audio_interface():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None
    )
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    return volume


class GestureController:
    def __init__(self, screen_w, screen_h, smooth=7):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.smooth = smooth

        self.prev_x = 0
        self.prev_y = 0

        try:
            self.volume = get_audio_interface()
            self.min_vol, self.max_vol = self.volume.GetVolumeRange()[:2]
            self.volume_enabled = True
        except:
            self.volume_enabled = False

    def fingers_up(self, lm):
        tips = [4, 8, 12, 16, 20]
        fingers = []

        lm_dict = {id: (x, y) for id, x, y in lm}

        fingers.append(1 if lm_dict[4][0] < lm_dict[3][0] else 0)

        for tip in tips[1:]:
            fingers.append(1 if lm_dict[tip][1] < lm_dict[tip - 2][1] else 0)

        return fingers

    def is_pinch(self, lm, threshold=40):
        lm_dict = {i: (x, y) for i, x, y in lm}
        if 4 in lm_dict and 8 in lm_dict:
            dist = np.hypot(lm_dict[8][0] - lm_dict[4][0],
                            lm_dict[8][1] - lm_dict[4][1])
            return dist < threshold, dist
        return False, None

    def set_volume(self, dist, min_d=20, max_d=150):
        if not self.volume_enabled:
            return

        dist = np.clip(dist, min_d, max_d)
        vol = np.interp(dist, [min_d, max_d], [self.min_vol, self.max_vol])
        self.volume.SetMasterVolumeLevel(vol, None)

    def set_brightness(self, dist, min_d=20, max_d=150):
        dist = np.clip(dist, min_d, max_d)
        bright = int(np.interp(dist, [min_d, max_d], [0, 100]))
        try:
            sbc.set_brightness(bright)
        except:
            pass

    def move_cursor(self, finger, frame_w, frame_h):
        _, x, y = finger
        sx = np.interp(x, [0, frame_w], [0, self.screen_w])
        sy = np.interp(y, [0, frame_h], [0, self.screen_h])

        curr_x = self.prev_x + (sx - self.prev_x) / self.smooth
        curr_y = self.prev_y + (sy - self.prev_y) / self.smooth

        pyautogui.moveTo(curr_x, curr_y)

        self.prev_x, self.prev_y = curr_x, curr_y

    def click(self):
        pyautogui.click()
