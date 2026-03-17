import cv2
from utils.fps_counter import FPSCounter
from hand_tracking.hand_detection import HandDetector
from gestures.finger_states import HandGesture
from modes.mode_manger import ModeManager
from controllers.volume import VolumeController
from controllers.keyboard import Keyboard


cap = cv2.VideoCapture(0)
fps_counter = FPSCounter()
detector = HandDetector()
mode_manager = ModeManager()
volume_controller = VolumeController()
keyboard_controller = Keyboard(cap, 720, 720)


while True:
    ret, frame = cap.read()
    if not ret:
        break

    newFrame = cv2.resize(frame, (960, 960))
    
    # Detect hands
    detection_result = detector.convert(newFrame)
    hand_landmarks_list, handedness_list, newFrame = detector.draw_landmarks_on_image(newFrame, detection_result)

    gesture_name = "No Gesture"
    # If hands are detected, process the first hand
    if hand_landmarks_list:
        gesture = HandGesture(hand_landmarks_list[0])
        gesture_name = gesture.get_gesture_name()
        
        # Update mode manager
        mode_manager.update(gesture_name)

        # Volume control if in Volume mode
        current_mode = mode_manager.get_current_mode()
        if current_mode == "Volume":
            volume_controller.update(hand_landmarks_list[0], newFrame)
        # Keyboard control if in Keyboard mode
        elif current_mode == "Keyboard":
            keyboard_controller.process_frame(newFrame)

    current_mode = mode_manager.get_current_mode()

    # Display the current mode on the image
    cv2.putText(newFrame, f"Mode: {current_mode}", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    cv2.putText(newFrame, f"Gesture: {gesture_name}", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    fps_counter.update()
    fps_counter.write_fps(newFrame)

    cv2.imshow('Webcam', newFrame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()