import cv2
import math
import pyautogui as pag

class VolumeController:
    def __init__(self):
        self.min_distance = 30  
        self.max_distance = 240 
        self.prev_volume = 20
        self.smoothed_volume = 15
        self.smoothing_factor = 0.7

    def calculate_distance(self, point1, point2, frame):
        h, w, _ = frame.shape

        x1, y1 = int(point1.x * w), int(point1.y * h)
        x2, y2 = int(point2.x * w), int(point2.y * h)

        distance = math.hypot(x2 - x1, y2 - y1)

        return distance, (x1, y1), (x2, y2)

    def get_volume_level(self, distance):
        distance = max(self.min_distance, min(self.max_distance, distance))

        volume = int(
            (distance - self.min_distance)
            / (self.max_distance - self.min_distance)
            * 100
        )

        return volume

    def set_system_volume(self, volume_level):
        difference = volume_level - self.prev_volume

        if abs(difference) < 2:
            return

        presses = min(abs(difference) // 2, 10)

        if difference > 0:
            for _ in range(presses):
                pag.press("volumeup")
        else:
            for _ in range(presses):
                pag.press("volumedown")

        self.prev_volume = volume_level

    def draw_volume_bar(self, frame, volume):
        bar_x, bar_y = 50, 250
        bar_width, bar_height = 30, 250

        fill_height = int((volume / 100) * bar_height)

        cv2.rectangle(
            frame,
            (bar_x, bar_y),
            (bar_x + bar_width, bar_y + bar_height),
            (255, 255, 255),
            2,
        )

        cv2.rectangle(
            frame,
            (bar_x, bar_y + bar_height - fill_height),
            (bar_x + bar_width, bar_y + bar_height),
            (0, 255, 0),
            -1,
        )

        cv2.putText(
            frame,
            f"Volume: {volume}%",
            (bar_x, bar_y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2,
        )

    def draw_pinch_feedback(self, frame, p1, p2):
        cv2.circle(frame, p1, 10, (255, 0, 255), -1)
        cv2.circle(frame, p2, 10, (255, 0, 255), -1)
        cv2.line(frame, p1, p2, (255, 0, 255), 3)

    def update(self, hand_landmarks, frame):
        if not hand_landmarks:
            return None

        thumb = hand_landmarks[4]
        index = hand_landmarks[8]

        distance, p1, p2 = self.calculate_distance(thumb, index, frame)

        volume = self.get_volume_level(distance)

        self.smoothed_volume = int(
            self.smoothing_factor * self.smoothed_volume
            + (1 - self.smoothing_factor) * volume
        )

        self.set_system_volume(self.smoothed_volume)

        self.draw_pinch_feedback(frame, p1, p2)
        self.draw_volume_bar(frame, self.smoothed_volume)

        return self.smoothed_volume