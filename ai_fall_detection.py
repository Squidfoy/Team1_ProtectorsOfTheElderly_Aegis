# We'll use the test_on_dataset.py's code to do prototype for midterm
# Than later use pose_test.py after we get live feed working
# Just need to modify it for admin.py
# For now I'll use this place holder code to test
# Last edited by: Alianna
# Last updated date: Wed Mar 11 2026
import os
import cv2
import numpy as np
from ultralytics import YOLO

# I chose v11 rather than v12 becuase 11 excels in accuracy and has faster CPU inference speeds
# (2.4 ms to 4.7 ms rather than 5.6 ms or higher on the 12), 
# making it good for systems without a specified GPU(like the raspberry pi) 
model = YOLO("yolo11n-pose.pt") 

def get_keypoint(keypoints, index):
    # # Get a keypoint's (x, y) coordinates.
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

# Use the Ai fall model to look at video
# Send result back to admin.py as boolean value
def fall_check(folder_dir, video_file_name):
    # Get the video location info
    file_path = os.path.join(folder_dir, video_file_name)
    print("At: ", file_path)
    print("Checking for fall in video: ", video_file_name)


    # Alianna you can out the ai model code here**************************************
    # Use the same test_on_dataset.py code
    # But instead of the dataset videos just use video_file_name or file_path
    cap = cv2.VideoCapture(file_path)

    fall_frame_count = 0
    FALL_FRAMES_THRESHOLD = 5
    fall_detected = False
    prev_hip_y = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_height = frame.shape[0]
        results = model(frame, verbose=False)

        fall_in_frame = False
        for result in results:
            if result.keypoints is not None:
                for person_keypoints in result.keypoints.data:
                    if is_fall(person_keypoints, frame_height, prev_hip_y):
                        fall_in_frame = True

                    # Update prev_hip_y AFTER checking for fall
                    try:
                        left_hip = get_keypoint(person_keypoints, 11)
                        right_hip = get_keypoint(person_keypoints, 12)
                        prev_hip_y = (left_hip[1] + right_hip[1]) // 2
                    except Exception:
                        pass

        if fall_in_frame:
            fall_frame_count += 1
        else:
            fall_frame_count = 0

        if fall_frame_count >= FALL_FRAMES_THRESHOLD:
            fall_detected = True
            break

    cap.release()

    # Return a result string back to admin.py
    if fall_detected:
        return f"FALL DETECTED in {video_file_name}"
    else:
        return f"No fall detected in {video_file_name}"
    # *****************************************************************


