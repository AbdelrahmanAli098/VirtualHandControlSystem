import cv2
import math
import time
from hand_tracking.hand_detection import HandDetector
from pynput.keyboard import Controller, Key
from modes.mode_manger import ModeManager


class Keyboard(ModeManager):
    KEY_SIZE       = 40          # px, square key face
    KEY_SPACING    = 10          # px, gap between keys
    KB_OFFSET_X    = 60          # px, keyboard left edge
    KB_OFFSET_Y    = 420         # px, keyboard top edge
    PINCH_THRESH   = 40          # px, index–middle distance to trigger press
    PRESS_COOLDOWN = 1        # seconds between consecutive presses
    KEYBOARD_LAYOUT = [
        ["1","2","3","4","5","6","7","8","9","0"],
        ["Q","W","E","R","T","Y","U","I","O","P"],
        ["A","S","D","F","G","H","J","K","L",";"],
        ["Z","X","C","V","B","N","M",",",".","/"],
        ["SPACE", "ENTER", "BACKSPACE"],
    ]

    # Special keys that are wider than a normal key
    WIDE_KEYS = {"SPACE": 3, "ENTER": 2, "BACKSPACE": 2}

    def __init__(self, camera, screen_width, screen_height):
        super().__init__()
        self.camera = camera
        self.screen_width  = screen_width
        self.screen_height = screen_height
        self.typed_text = ""
        self.detector = HandDetector()
        self.keyboard = Controller()
        self.last_press_time = 0
        self.button_list = self.build_button_list()

    def build_button_list(self):
        buttons = []
        step = self.KEY_SIZE + self.KEY_SPACING

        for row_i, row in enumerate(self.KEYBOARD_LAYOUT):
            col_x = self.KB_OFFSET_X
            for key in row:
                multiplier = self.WIDE_KEYS.get(key, 1)
                w = self.KEY_SIZE * multiplier + self.KEY_SPACING * (multiplier - 1)
                y = self.KB_OFFSET_Y + row_i * step
                buttons.append((key, col_x, y, w, self.KEY_SIZE))
                col_x += w + self.KEY_SPACING

        return buttons

    def draw_keyboard(self, img):
        overlay = img.copy()
        # Draw keys
        for key, x, y, w, h in self.button_list:
            cv2.rectangle(overlay, (x, y), (x + w, y + h), (50, 50, 50), -1)
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 150, 150), 2)
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.55 if len(key) == 1 else 0.42
            (tw, th), _ = cv2.getTextSize(key, font, font_scale, 1)
            tx = x + (w - tw) // 2
            ty = y + (h + th) // 2
            cv2.putText(img, key, (tx, ty), font, font_scale,(255, 255, 255), 1, cv2.LINE_AA)
        # Draw typed text area
        cv2.addWeighted(overlay, 0.45, img, 0.55, 0, img)
        bar_y = self.KB_OFFSET_Y - 55
        cv2.rectangle(img,(self.KB_OFFSET_X, bar_y),(self.KB_OFFSET_X + 620, bar_y + 42),(20, 20, 20), -1)
        cv2.rectangle(img,(self.KB_OFFSET_X, bar_y),(self.KB_OFFSET_X + 620, bar_y + 42),(180, 180, 180), 1)
        cv2.putText(img, self.typed_text[-60:],(self.KB_OFFSET_X + 6, bar_y + 30),cv2.FONT_HERSHEY_SIMPLEX, 0.7,(0, 255, 180), 2, cv2.LINE_AA)

        return img
    
    def highlight_key(self, img, key, x, y, w, h):
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 200, 255), -1)
        font       = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.55 if len(key) == 1 else 0.42
        (tw, th), _ = cv2.getTextSize(key, font, font_scale, 1)
        tx = x + (w - tw) // 2
        ty = y + (h + th) // 2
        cv2.putText(img, key, (tx, ty), font, font_scale,
                    (0, 0, 0), 2, cv2.LINE_AA)

    def get_hovered_key(self, fx, fy):
        for key, x, y, w, h in self.button_list:
            if x <= fx <= x + w and y <= fy <= y + h:
                return key, x, y, w, h
        return None

    def press_key(self, key):
        if key == "SPACE":
            self.keyboard.press(Key.space)
            self.keyboard.release(Key.space)
            self.typed_text += " "
        elif key == "ENTER":
            self.keyboard.press(Key.enter)
            self.keyboard.release(Key.enter)
            self.typed_text += "\n"
        elif key == "BACKSPACE":
            self.keyboard.press(Key.backspace)
            self.keyboard.release(Key.backspace)
            if self.typed_text:
                self.typed_text = self.typed_text[:-1]
        else:
            self.keyboard.press(key)
            self.keyboard.release(key)
            self.typed_text += key

    def process_frame(self, img):
        # 1. Draw keyboard
        img = self.draw_keyboard(img)

        # 2. Detect hands
        hands = self.detector.convert(img).hand_landmarks
        if not hands:
            return img      
        
        # 3. First detected hand
        hand = hands[0]

        # Index fingertip — landmark 8
        ix = int(hand[8].x * self.screen_width)
        iy = int(hand[8].y * self.screen_height)

        # Middle fingertip — landmark 12 (for pinch)
        mx = int(hand[12].x * self.screen_width)
        my = int(hand[12].y * self.screen_height)

        distance = math.hypot(ix - mx, iy - my)

        # Draw fingertip cursor
        cv2.circle(img, (ix, iy), 10, (0, 255, 0), cv2.FILLED)

        # 4. Hover highlight
        hovered = self.get_hovered_key(ix, iy)
        if hovered:
            key, kx, ky, kw, kh = hovered
            self.highlight_key(img, key, kx, ky, kw, kh)

            # 5. Pinch = press (timestamp cooldown — no sleep!)
            now = time.time()
            if distance < self.PINCH_THRESH and (now - self.last_press_time) > self.PRESS_COOLDOWN:
                cv2.circle(img, (ix, iy), 18, (0, 0, 255), cv2.FILLED)
                self.press_key(key)
                self.last_press_time = now

        return img