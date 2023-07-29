import csv, copy, argparse, itertools
import cv2 as cv
import numpy as np
import mediapipe as mp
from utils.hands import Hand
from utils.fans import Fan

def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--d', type=bool, default=True, help='Debug mode')

    parser.add_argument('--device', type=int, default=0, help='Device index')
    parser.add_argument('--width', type=int, default=1280, help='Capture width')
    parser.add_argument('--height', type=int, default=800, help='Capture height')

    parser.add_argument('--use_static_image_mode', action='store_true', help='Use static image mode')
    parser.add_argument('--min_detection_confidence', type=float, default=0.5, help='Min detection confidence')
    parser.add_argument('--min_tracking_confidence', type=float, default=0.5, help='Min tracking confidence')


    args = parser.parse_args()

    return args

def main():
    args = get_args()

    debug = args.d

    cap_device = args.device
    cap_width = args.width
    cap_height = args.height

    use_static_image_mode = args.use_static_image_mode
    min_detection_confidence = args.min_detection_confidence
    min_tracking_confidence = args.min_tracking_confidence

    mp_drawing = mp.solutions.drawing_utils
    mp_hands = mp.solutions.hands

    cap = cv.VideoCapture(cap_device)
    cap.set(cv.CAP_PROP_FRAME_WIDTH, cap_width)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, cap_height)

    hands = mp_hands.Hands(
        static_image_mode=use_static_image_mode,
        max_num_hands=1,
        min_detection_confidence=min_detection_confidence,
        min_tracking_confidence=min_tracking_confidence)
    
    hand = Hand()
    hand.image_width = cap_width
    hand.image_height = cap_height
    
    gesture_history = ['None', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None']
    gesture_idx = 0

    fan = Fan(servoVPin = 12, servoHPin = 7, speedPin = 18, APin = 14, BPin = 15)


    while True:

        key = cv.waitKey(10)
        if key == 27:  # ESC
            break

        # --- image processing --- #
        ret, image = cap.read()
        if not ret:
            break
        image = cv.flip(image, 1)
        debug_image = copy.deepcopy(image) if debug else None
        image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = hands.process(image)
        image.flags.writeable = True
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                hand.update_landmarks(hand_landmarks)
                if debug:
                    mp_drawing.draw_landmarks(
                        debug_image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        else:
            hand.gesture = 'None'
        # --- image processing finished ---#

        gesture_history[gesture_idx] = hand.gesture
        gesture = hand.gesture if gesture_history.count(hand.gesture) > 5 else 'None'

        fan.control(gesture)
        gesture_idx = (gesture_idx + 1) % 10

        if debug_image is not None:
            debug_image = cv.putText(debug_image, hand.get_state_str(), (10, 30), cv.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2, cv.LINE_AA)
            debug_image = cv.putText(debug_image, hand.gesture, (10, 60), cv.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2, cv.LINE_AA)
            debug_image = cv.putText(debug_image, gesture, (10, 90), cv.FONT_HERSHEY_SIMPLEX, 1.0, (255, 0, 0), 2, cv.LINE_AA)
            debug_image = cv.putText(debug_image, fan.state_str, (10, 110), cv.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2, cv.LINE_AA )
            cv.imshow('MediaPipe Hands', debug_image)



    cap.release()
    cv.destroyAllWindows()



if __name__ == '__main__':
    main()