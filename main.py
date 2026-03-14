import cv2
import time
from utils.fps_counter import FPSCounter
from hand_tracking.hand_detection import HandDetector
from gestures.finger_states import HandGesture

cap = cv2.VideoCapture(0)
fps_counter = FPSCounter()
detector = HandDetector()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    newFrame = cv2.resize(frame, (950, 750))
    
    # Detect hands
    detection_result = detector.convert(newFrame)
    hand_landmarks_list, handedness_list, newFrame = detector.draw_landmarks_on_image(newFrame, detection_result)

    # If hands are detected, process the first hand
    if hand_landmarks_list:
        gesture = HandGesture(hand_landmarks_list[0])
        gesture_name = gesture.get_gesture_name()
        
        # Display the gesture name on the image
        cv2.putText(newFrame, f"Gesture: {gesture_name}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    fps_counter.update()
    fps_counter.write_fps(newFrame)

    cv2.imshow('Webcam', newFrame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()