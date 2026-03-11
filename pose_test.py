# this should open your webcam and draw a skeleton overlay on any person it detects — 17 keypoints 
# like shoulders, hips, knees, ankles, etc.

# This is Open Source Computer Vision Library. It is used for real-time computer vision applications.
import cv2
import numpy as np
from ultralytics import YOLO

# Load the YOLOv11 pose model (downloads automatically first time)
model = YOLO("yolov11n-pose.pt")

# Open your webcam (0 = default camera)
cap = cv2.VideoCapture(0)

def get_keypoint(keypoints, index):
    # Get a keypoint's (x, y) coordinates.
    kp = keypoints[index]
    return int(kp[0]), int(kp[1])

def calculate_angle(p1, p2):
    # Calculate the angle (in degrees) of the line between two points.
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    angle = abs(np.degrees(np.arctan2(dy, dx)))
    return angle

def is_fall(keypoints, frame_height, prev_hip_y=None):
    """
    Fall detection logic using shoulder and hip keypoints.
    Returns True if a fall is detected.
    
    YOLOv8 keypoint indices:
    5 = left shoulder, 6 = right shoulder
    11 = left hip, 12 = right hip
    """
    try:
        left_shoulder = get_keypoint(keypoints, 5)
        right_shoulder = get_keypoint(keypoints, 6)
        left_hip = get_keypoint(keypoints, 11)
        right_hip = get_keypoint(keypoints, 12)

        # Get the midpoints of shoulders and hips
        shoulder_mid = ((left_shoulder[0] + right_shoulder[0]) // 2,
                        (left_shoulder[1] + right_shoulder[1]) // 2)
        hip_mid = ((left_hip[0] + right_hip[0]) // 2,
                   (left_hip[1] + right_hip[1]) // 2)

        # Calculate the angle of the torso
        torso_angle = calculate_angle(shoulder_mid, hip_mid)

        # Calculate how low the hips are relative to the frame
        hip_height_ratio = hip_mid[1] / frame_height

        # Fall conditions:
        # 1. Torso is close to horizontal (angle near 0 or 180)
        # 2. Hips are in the lower 70% of the frame
        torso_is_horizontal = torso_angle < 30 or torso_angle > 150
        hips_are_low = hip_height_ratio > 0.7

        # Check for rapid downward drop
        rapid_drop = False
        if prev_hip_y is not None:
            drop_amount = hip_mid[1] - prev_hip_y
            drop_ratio = drop_amount / frame_height
            rapid_drop = drop_ratio > 0.05

        return (torso_is_horizontal and hips_are_low) or (rapid_drop and hips_are_low)

    except Exception:
        return False

frame_height = None
fall_frame_count = 0
FALL_FRAMES_THRESHOLD = 5  # Fall must persist for 5 frames to avoid false positives
prev_hip_y = None

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_height = frame.shape[0]
    results = model(frame, verbose=False)
    annotated_frame = results[0].plot()

    fall_detected = False

    # Loop through each detected person
    for result in results:
        if result.keypoints is not None:
            for person_keypoints in result.keypoints.data:
                if is_fall(person_keypoints, frame_height):
                    fall_detected = True
                # Update prev_hip_y AFTER checking for fall
                try:
                    left_hip = get_keypoint(person_keypoints, 11)
                    right_hip = get_keypoint(person_keypoints, 12)
                    prev_hip_y = (left_hip[1] + right_hip[1]) // 2
                except Exception:
                    pass

    # Require the fall to persist across multiple frames
    if fall_detected:
        fall_frame_count += 1
    else:
        fall_frame_count = 0

    # If a fall is detected, show an alert
    if fall_frame_count >= FALL_FRAMES_THRESHOLD:
        cv2.putText(annotated_frame, "FALL DETECTED!", (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)

    cv2.imshow("Aegis - Fall Detection", annotated_frame)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()


    


