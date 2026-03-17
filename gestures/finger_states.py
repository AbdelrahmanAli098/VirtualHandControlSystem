import mediapipe as mp


class HandGesture:
    def __init__(self, hand_landmarks):
        self.hand_landmarks = hand_landmarks
        self.finger_states = self.get_finger_states(hand_landmarks)

    def get_finger_states(self, hand_landmarks):
        finger_states = []
        
        # Define the indices for the fingertips and their corresponding joints
        fingertip_indices = [8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky
        joint_indices = [6, 10, 14, 18]       # Corresponding joints for each finger

        thumb_tip_index = 4
        thumb_joint_index = 2

        # Check thumb separately because it moves differently than the other fingers
        thumb_tip_x = hand_landmarks[thumb_tip_index].x
        thumb_joint_x = hand_landmarks[thumb_joint_index].x
        if thumb_tip_x < thumb_joint_x:
            finger_states.append(1)  
        else:
            finger_states.append(0)  

        for tip_idx, joint_idx in zip(fingertip_indices, joint_indices):
            tip_x = hand_landmarks[tip_idx].y
            joint_x = hand_landmarks[joint_idx].y

            if tip_x < joint_x:
                finger_states.append(1)
            else:
                finger_states.append(0)

        return finger_states

    def get_gesture_name(self):
        if self.finger_states == [1, 1, 0, 0, 0]:
            return "Volume mode"
        elif self.finger_states == [0, 0, 1, 1, 1]:
            return "Keyboard mode"
        else:
            return "Unknown Gesture"