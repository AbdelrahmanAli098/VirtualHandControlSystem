import time 
import cv2


class FPSCounter:
    # This class is used to calculate and display the frames per second (FPS) of a video stream.
    def __init__(self):
        self.start_time = time.time()
        self.frame_count = 0
    # The update method increments the frame count each time a new frame is processed.
    def update(self):
        self.frame_count += 1
    # The get_fps method calculates the FPS by dividing the total number of frames by the elapsed time since the start.
    def get_fps(self):
        elapsed_time = time.time() - self.start_time
        if elapsed_time > 0:
            return self.frame_count // elapsed_time
        else:
            return 0.0    
    def write_fps(self, frame):
        fps = self.get_fps()
        cv2.putText(frame, f'FPS: {int(fps)}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

