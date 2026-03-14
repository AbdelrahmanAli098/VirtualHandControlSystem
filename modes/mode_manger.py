import time

class ModeManager:
    def __init__(self):
        self.current_mode = "Default"
        self.mode_gestures = {
            "Click": "Click",
            "Pointing": "Pointing",
            "Volume mode": "Volume",
            "Keyboard mode": "Keyboard",
        }
        self.last_gesture = None
        self.gesture_start_time = None
        self.hold_duration = 2.0  # seconds

    def update(self, gesture_name):
        if gesture_name in self.mode_gestures:
            if self.last_gesture != gesture_name:
                # New gesture detected, start timer
                self.last_gesture = gesture_name
                self.gesture_start_time = time.time()
            else:
                # Same gesture, check if held long enough
                if time.time() - self.gesture_start_time >= self.hold_duration:
                    self.current_mode = self.mode_gestures[gesture_name]
                    # Reset to avoid repeated switches
                    self.last_gesture = None
                    self.gesture_start_time = None
        else:
            # Not a mode gesture, reset
            self.last_gesture = None
            self.gesture_start_time = None

    def get_current_mode(self):
        return self.current_mode