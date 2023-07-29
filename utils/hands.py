import numpy as np

class Hand:
    def __init__(self):
        self.landmarks = None
        self.landmark_list = []
        self.image_width = 0
        self.image_height = 0
        self.state = None
        self.state_str = ''
        self.location = None
        self.gesture = 'None'

    def update_landmarks(self, landmarks):
        self.landmarks = landmarks
        self.landmark_list = self.calc_landmark_list()
        self.update_hand_state()
        self.update_location()
        self.update_gesture()

    def calc_landmark_list(self):
        landmark_points = []
        for _, lm in enumerate(self.landmarks.landmark):
            x = min(int(lm.x * self.image_width), self.image_width - 1)
            y = min(int(lm.y * self.image_height), self.image_height - 1)
            landmark_points.append([x, y])
        return landmark_points

    def get_state_str(self):
        state = self.state
        if state is None:
            return ''
        directions = ['U', 'D', 'L', 'R']
        ret = directions[state[0]] + ", " + directions[state[1]] + " / "
        for i in range(2, 7):
            if state[i]:
                ret += 'O'
            else:
                ret += '.'
        return ret
        
    
    def get_hand_state(self):
        return self.update_hand_state()
    
    def update_hand_state(self):
        hand_direction = self.get_hand_direction()
        finger_state = self.get_finger_state()
        self.state = hand_direction + finger_state
        return self.state

    def get_finger_state(self):
        ret = [False, False, False, False, False]
        for i in range(5):
            ret[i] = self.is_finger_spread(self.landmark_list[0], self.landmark_list[4*i+1], self.landmark_list[4*i+2], self.landmark_list[4*i+3], self.landmark_list[4*i+4])

        return ret

    def is_finger_spread(self, p0, p1, p2, p3, p4):
        v1 = np.subtract(p1, p0)
        v2 = np.subtract(p2, p1)
        v3 = np.subtract(p3, p2)
        v4 = np.subtract(p4, p3)

        d1 = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
        d2 = np.dot(v2, v3) / (np.linalg.norm(v2) * np.linalg.norm(v3))
        d3 = np.dot(v3, v4) / (np.linalg.norm(v3) * np.linalg.norm(v4))
        d4 = np.dot(v4, v2) / (np.linalg.norm(v4) * np.linalg.norm(v2))

        return d1 > 0.3 and d2 > 0.5 and d3 > 0.5 and d4 > 0.5
        # return d2 > 0.5 and d3 > 0.5 and d4 > 0.5
    
    def get_hand_direction(self):
        # 0: up, 1: down, 2: left, 3: right
        ret1 = -1
        ret2 = -1
        vec1 = np.subtract(self.landmark_list[9], self.landmark_list[0]) 
        vec2 = np.subtract(self.landmark_list[5], self.landmark_list[17])

        vertical1 = np.dot(vec1, [0,1])/ np.linalg.norm(vec1)
        vertical2 = np.dot(vec2, [0,1])/ np.linalg.norm(vec2)
        horizontal1 = np.dot(vec1, [1,0])/ np.linalg.norm(vec1)
        horizontal2 = np.dot(vec2, [1,0])/ np.linalg.norm(vec2)
        
        if vertical1 < -0.85 :
            ret1 = 0
        elif vertical1 > 0.5:
            ret1 = 1
        elif horizontal1 > 0:
            ret1 = 2
        else:
            ret1 = 3

        if vertical2 < -0.85 :
            ret2 = 0
        elif vertical2 > 0.5:
            ret2 = 1
        elif horizontal2 > 0:
            ret2 = 2
        else:
            ret2 = 3
        return [ret1, ret2]
    
    def get_location(self):
        return self.update_hand_location()
    
    def update_location(self):
        self.location = np.add(self.landmark_list[0], self.landmark_list[9]) // 2
        return self.location
    
    def get_gesture(self):
        return self.update_gesture()
    
    def update_gesture(self):
        self.gesture = gesture_lut.get(tuple(self.state), 'None')
        return self.gesture

# Directions - 0: up, 1: down, 2: left, 3: right
gesture_lut = {
    (0, 3, True, True, True, True, True) : 'HighFive',
    (0, 3, False, True, False, False, False) : 'One',
    (0, 3, False, True, True, False, False) : 'Two',
    (0, 3, False, True, True, True, False) : 'Three',
    (0, 3, False, True, True, True, True) : 'Four',
    (0, 3, False, False, False, False, False) : 'Fist',
    (0, 2, False, False, False, False, False) : 'Fist',
    (0, 0, True, False, False, False, False) : 'ThumbUp',
    (2, 0, True, False, False, False, False) : 'ThumbUp',
    (3, 0, True, False, False, False, False) : 'ThumbUp',
    (0, 1, True, False, False, False, False) : 'ThumbDown',
    (2, 1, True, False, False, False, False) : 'ThumbDown',
    (3, 1, True, False, False, False, False) : 'ThumbDown',
    (0, 2, True, False, False, False, False) : 'ThumbLeft',
    (1, 2, True, False, False, False, False) : 'ThumbLeft',
    (2, 2, True, False, False, False, False) : 'ThumbLeft',
    (0, 3, True, False, False, False, False) : 'ThumbRight',
    (1, 3, True, False, False, False, False) : 'ThumbRight',
    (3, 3, True, False, False, False, False) : 'ThumbRight',
    (0, 2, True, True, False, False, False) : 'UpArrow',
    (0, 3, True, True, False, False, False) : 'UpArrow',
    (1, 2, True, True, False, False, False) : 'DownArrow',
    (3, 3, True, True, False, False, False) : 'DownArrow',
    (2, 2, True, True, False, False, False) : 'DownArrow',
    (1, 3, True, True, False, False, False) : 'DownArrow',
    (2, 0, True, True, False, False, False) : 'LeftArrow',
    (3, 0, True, True, False, False, False) : 'RightArrow',
    (0, 2, True, True, True, False, False) : 'UpTripleArrow',
    (0, 3, True, True, True, False, False) : 'UpTripleArrow',
    (1, 2, True, True, True, False, False) : 'DownTripleArrow',
    (3, 3, True, True, True, False, False) : 'DownTripleArrow',
    (2, 2, True, True, True, False, False) : 'DownTripleArrow',
    (1, 3, True, True, True, False, False) : 'DownTripleArrow',
    (2, 0, True, True, True, False, False) : 'LeftTripleArrow',
    (3, 0, True, True, True, False, False) : 'RightTripleArrow',
    (0, 0, True, True, True, True, True) : 'Salute',
    # (0, 3, True, True, True, True, True) : 'Salute',
    (3, 0, True, True, True, True, True) : 'Salute',
    (3, 3, True, True, True, True, True) : 'Salute',
}