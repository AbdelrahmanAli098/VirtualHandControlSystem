import cv2
import math
import pyautogui as pag

class VolumeController:
    def __init__(self):
        self.min_distance = 50  # Minimum distance for volume 0
        self.max_distance = 200  # Maximum distance for volume 100
        self.prev_volume = 50

    def calculate_distance(self, point1, point2):
        x1, y1 = point1.x * 640, point1.y * 480  # Assuming frame size
        x2, y2 = point2.x * 640, point2.y * 480
        distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        return distance

    def get_volume_level(self, distance):
        if distance < self.min_distance:
            return 0
        elif distance > self.max_distance:
            return 100
        else:
            return int((distance - self.min_distance) / (self.max_distance - self.min_distance) * 100)

    def set_system_volume(self, volume_level):
        # Use keyboard simulation to adjust volume
        if volume_level > self.prev_volume + 10:
            pag.press('volumeup')
            self.prev_volume = volume_level
        elif volume_level < self.prev_volume - 10:
            pag.press('volumedown')
            self.prev_volume = volume_level

    def draw_volume_bar(self, frame, volume):
        bar_x, bar_y = 50, 50
        bar_width, bar_height = 20, 200
        fill_height = int((volume / 100) * bar_height)
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (255, 255, 255), 2)
        cv2.rectangle(frame, (bar_x, bar_y + bar_height - fill_height), (bar_x + bar_width, bar_y + bar_height), (0, 255, 0), -1)
        cv2.putText(frame, f"Volume: {volume}%", (bar_x, bar_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    def update(self, hand_landmarks, frame):
        if hand_landmarks:
            thumb = hand_landmarks[4]
            index = hand_landmarks[8]
            distance = self.calculate_distance(thumb, index)
            volume = self.get_volume_level(distance)
            self.set_system_volume(volume)
            self.draw_volume_bar(frame, volume)
            return volume
        return None
