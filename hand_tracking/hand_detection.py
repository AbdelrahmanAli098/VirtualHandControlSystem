import mediapipe as mp
import cv2
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

class HandDetector:
    def __init__(self):
        self.base_options = python.BaseOptions(model_asset_path='hand_tracking/hand_landmarker.task')
        self.options = vision.HandLandmarkerOptions(base_options=self.base_options, num_hands=2)
        self.detector = vision.HandLandmarker.create_from_options(self.options)
        self.mp_hands = mp.tasks.vision.HandLandmarksConnections
        self.mp_drawing = mp.tasks.vision.drawing_utils
        self.mp_drawing_styles = mp.tasks.vision.drawing_styles

    def convert(self, frame):
        imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=imgRGB)
        detection = self.detector.detect(mp_image)
        return detection

    def draw_landmarks_on_image(self, imgRGB, detection_result):
        hand_landmarks_list = detection_result.hand_landmarks
        handedness_list = detection_result.handedness
        annotated_image = imgRGB.copy()
        
        # Draw landmarks using MediaPipe's drawing utils
        for hand_landmarks in hand_landmarks_list:
            self.mp_drawing.draw_landmarks(
                annotated_image,
                hand_landmarks,
                self.mp_hands.HAND_CONNECTIONS,
                self.mp_drawing_styles.get_default_hand_landmarks_style(),
                self.mp_drawing_styles.get_default_hand_connections_style()
            )
        
        return hand_landmarks_list, handedness_list, annotated_image

