# Very similar to post_test but this works on video files instead of webcam feed.
import cv2
import numpy as np
from ultralytics import YOLO

# I chose v11 rather than v12 becuase 11 excels in accuracy and has faster CPU inference speeds
# (2.4 ms to 4.7 ms rather than 5.6 ms or higher on the 12), 
# making it good for systems without a specified GPU(like the raspberry pi) 
model = YOLO("yolo11n-pose.pt")  

def get_keypoint(keypoints, index):
    kp = keypoints[index]
    return int(kp[0]), int(kp[1])

def calculate_angle(p1, p2):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    angle = abs(np.degrees(np.arctan2(dy, dx)))
    return angle

def is_fall(keypoints, frame_height, prev_hip_y=None):
    try:
        left_shoulder = get_keypoint(keypoints, 5)
        right_shoulder = get_keypoint(keypoints, 6)
        left_hip = get_keypoint(keypoints, 11)
        right_hip = get_keypoint(keypoints, 12)

        shoulder_mid = ((left_shoulder[0] + right_shoulder[0]) // 2,
                        (left_shoulder[1] + right_shoulder[1]) // 2)
        hip_mid = ((left_hip[0] + right_hip[0]) // 2,
                   (left_hip[1] + right_hip[1]) // 2)

        torso_angle = calculate_angle(shoulder_mid, hip_mid)
        hip_height_ratio = hip_mid[1] / frame_height

        torso_is_horizontal = torso_angle < 30 or torso_angle > 150 
        hips_are_low = hip_height_ratio > 0.7 

        rapid_drop = False
        if prev_hip_y is not None:
            drop_amount = hip_mid[1] - prev_hip_y
            drop_ratio = drop_amount / frame_height
            rapid_drop = drop_ratio > 0.05

        return (torso_is_horizontal and hips_are_low) or (rapid_drop and hips_are_low)

    except Exception:
        return False

def test_video(video_path, expected_label):
    """
    Run fall detection on a video file and print results.
    expected_label: "fall" or "no_fall"
    """
    cap = cv2.VideoCapture(video_path)
    fall_frame_count = 0
    total_frames = 0
    FALL_FRAMES_THRESHOLD = 5 
    fall_detected_in_video = False
    prev_hip_y = None  # Track previous hip y-coordinate for rapid drop detection

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        total_frames += 1
        frame_height = frame.shape[0]
        results = model(frame, verbose=False)

        fall_in_frame = False
        for result in results:
            if result.keypoints is not None:
                for person_keypoints in result.keypoints.data:
                    if is_fall(person_keypoints, frame_height):
                        fall_in_frame = True
                    # Update prev_hip_y for next frame
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
            fall_detected_in_video = True
            break  # We don't need to keep checking once fall is confirmed

    cap.release()

    # Classify result into TP, TN, FP, FN
    if fall_detected_in_video and expected_label == "fall":
        result_type = "TP"
    elif not fall_detected_in_video and expected_label == "no_fall":
        result_type = "TN"
    elif fall_detected_in_video and expected_label == "no_fall":
        result_type = "FP"
    else:
        result_type = "FN"
    
    detected = "FALL" if fall_detected_in_video else "NO FALL"
    correct = result_type in ("TP", "TN")
    status = "CORRECT" if correct else "WRONG"
    print(f"{status} [{result_type}] | Expected: {expected_label.upper()} | Got: {detected} | File: {video_path}")

    return result_type

def run_all_tests():
    import os

    counts = {"TP": 0, "TN": 0, "FP": 0, "FN": 0}

    # Test fall videos only works on mp4, avi, mov files
    fall_dir = "test_videos/falls"
    for filename in os.listdir(fall_dir):
        if filename.endswith((".mp4", ".avi", ".mov")):
            result_type = test_video(os.path.join(fall_dir, filename), "fall")
            counts[result_type] += 1

    # Test no fall videos on mp4, avi, mov files
    no_fall_dir = "test_videos/no_falls"
    for filename in os.listdir(no_fall_dir):
        if filename.endswith((".mp4", ".avi", ".mov")):
            result_type = test_video(os.path.join(no_fall_dir, filename), "no_fall")
            counts[result_type] += 1

    # Calculate metrics
    TP, TN, FP, FN = counts["TP"], counts["TN"], counts["FP"], counts["FN"]
    total = TP + TN + FP + FN

    accuracy  = (TP + TN) / total * 100 if total > 0 else 0
    precision = TP / (TP + FP) * 100 if (TP + FP) > 0 else 0
    recall    = TP / (TP + FN) * 100 if (TP + FN) > 0 else 0
    f1        = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    fpr       = FP / (FP + TN) * 100 if (FP + TN) > 0 else 0  # false positive rate
    fnr       = FN / (FN + TP) * 100 if (FN + TP) > 0 else 0  # false negative rate

    print(f"\n--- Confusion Matrix ---")
    print(f"  TP: {TP}  |  FP: {FP}")
    print(f"  FN: {FN}  |  TN: {TN}")
    print(f"\n--- Metrics ---")
    print(f"Accuracy:           {accuracy:.1f}%")
    # of all the times we said "fall", how many were actually falls?
    print(f"Precision:          {precision:.1f}%") 
    # of all the actual falls, how many did we correctly identify as falls? (more important than precision)
    print(f"Recall:             {recall:.1f}%")
    # The harmonic mean of precision and recall, gives a single score that balances both concerns
    print(f"F1 Score:           {f1:.1f}%")
    print(f"False Positive Rate:{fpr:.1f}%")
    print(f"False Negative Rate:{fnr:.1f}%")
    print(f"\nTotal videos tested: {total}")

if __name__ == "__main__":
    run_all_tests()
