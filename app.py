import cv2
import mediapipe as mp
import math
import random

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# Set up video capture
cap = cv2.VideoCapture(0)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Set DPI scaling factor
dpi_scaling_factor = 6  # Adjust this scaling factor as needed

# Lists to store fireballs for each hand
fireballs_left = []
fireballs_right = []

# List to store zombies
zombies = []

# Function to generate fireballs
def generate_fireball(hand, x, y, angle):
    if hand == 'left':
        fireballs_left.append({'x': x, 'y': y, 'angle': angle})
    elif hand == 'right':
        fireballs_right.append({'x': x, 'y': y, 'angle': angle})

# Function to generate zombies
def generate_zombie():
    x = random.randint(50, width-100)
    y = random.randint(50, height-100)
    zombies.append({'x': x, 'y': y, 'dx': random.choice([-1, 1]), 'dy': random.choice([-1, 1])})

# Function to check collision between two rectangles
def check_collision(rect1, rect2):
    if (rect1['x'] < rect2['x'] + 50 and
        rect1['x'] + 50 > rect2['x'] and
        rect1['y'] < rect2['y'] + 50 and
        rect1['y'] + 50 > rect2['y']):
        return True
    return False

# Set up MediaPipe Hands
with mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5, max_num_hands=2) as hands:
    while cap.isOpened():
        success, image = cap.read()

        if not success:
            print("Ignoring empty camera frame.")
            continue

        # Flip image horizontally for natural hand movement
        image = cv2.flip(image, 1)
        # Convert BGR image to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Process the hand landmarks
        results = hands.process(image_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Extract hand landmarks
                hand = 'left' if hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].x < 0.5 else 'right'
                index_landmark = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                wrist_landmark = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
                index_x = int(index_landmark.x * width)
                index_y = int(index_landmark.y * height)
                wrist_x = int(wrist_landmark.x * width)
                wrist_y = int(wrist_landmark.y * height)

                # Adjust the starting position of fireballs towards the index finger tip
                fireball_start_x = index_x + int((wrist_x - index_x) * 0.2)  # 20% towards the index finger
                fireball_start_y = index_y + int((wrist_y - index_y) * 0.2)  # 20% towards the index finger

                # Calculate the angle of the fireball
                angle = math.atan2(wrist_y - index_y, wrist_x - index_x) - math.pi  # Reverse the direction

                # Generate fireball
                generate_fireball(hand, fireball_start_x, fireball_start_y, angle)  # Generate fireball from wrist

                # Draw hand landmarks
                mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        # Generate zombies randomly
        if random.random() < 0.1:  # Adjust this probability as needed
            generate_zombie()

        # Draw fireballs for left hand
        for fireball in fireballs_left:
            fireball_x = fireball['x']
            fireball_y = fireball['y']
            angle = fireball['angle']
            fireball_x += int(10 * math.cos(angle))
            fireball_y += int(10 * math.sin(angle))
            cv2.circle(image, (fireball_x, fireball_y), 10, (0, 0, 255), -1)
            fireball['x'] = fireball_x
            fireball['y'] = fireball_y

            if fireball_x < 0 or fireball_x > width or fireball_y < 0 or fireball_y > height:
                fireballs_left.remove(fireball)

        # Draw fireballs for right hand
        for fireball in fireballs_right:
            fireball_x = fireball['x']
            fireball_y = fireball['y']
            angle = fireball['angle']
            fireball_x += int(10 * math.cos(angle))
            fireball_y += int(10 * math.sin(angle))
            cv2.circle(image, (fireball_x, fireball_y), 10, (0, 0, 255), -1)
            fireball['x'] = fireball_x
            fireball['y'] = fireball_y

            if fireball_x < 0 or fireball_x > width or fireball_y < 0 or fireball_y > height:
                fireballs_right.remove(fireball)

        # Move zombies
        for zombie in zombies:
            zombie['x'] += zombie['dx']
            zombie['y'] += zombie['dy']

            # Check boundaries
            if zombie['x'] <= 0 or zombie['x'] >= width - 50:
                zombie['dx'] *= -1
            if zombie['y'] <= 0 or zombie['y'] >= height - 50:
                zombie['dy'] *= -1

            cv2.rectangle(image, (zombie['x'], zombie['y']), (zombie['x']+50, zombie['y']+50), (0, 255, 0), -1)

        # Check for collisions between fireballs and zombies
        for fireball in fireballs_left + fireballs_right:
            for zombie in zombies:
                if check_collision(fireball, zombie):
                    zombies.remove(zombie)

        # Display the image
        cv2.namedWindow('MediaPipe Hands', cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty('MediaPipe Hands', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.imshow('MediaPipe Hands', image)

        # Check for ESC key press to exit
        if cv2.waitKey(5) & 0xFF == 27:
            break

# Release the video capture object
cap.release()
cv2.destroyAllWindows()
