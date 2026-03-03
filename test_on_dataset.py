# Very similar to post_test but this works on video files instead of webcam feed.
import cv2
import numpy as np
from ultralytics import YOLO

model = YOLO("yolov8n-pose.pt")

def get_keypoint(keypoints, index):
    kp = keypoints[index]
    return int(kp[0]), int(kp[1])

def calculate_angle(p1, p2):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    angle = abs(np.degrees(np.arctan2(dy, dx)))
    return angle

def is_fall(keypoints, frame_height):
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

        return torso_is_horizontal and hips_are_low

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
    FALL_FRAMES_THRESHOLD = 10 
    fall_detected_in_video = False

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

        if fall_in_frame:
            fall_frame_count += 1
        else:
            fall_frame_count = 0

        if fall_frame_count >= FALL_FRAMES_THRESHOLD:
            fall_detected_in_video = True
            break  # We don't need to keep checking once fall is confirmed

    cap.release()

    # Determine if the result was correct
    correct = (fall_detected_in_video and expected_label == "fall") or \
              (not fall_detected_in_video and expected_label == "no_fall")

    status = "CORRECT" if correct else "WRONG"
    detected = "FALL" if fall_detected_in_video else "NO FALL"
    print(f"{status} | Expected: {expected_label.upper()} | Got: {detected} | File: {video_path}")

    return correct

def run_all_tests():
    import os

    results = {"correct": 0, "total": 0}

    # Test fall videos - only works on mp4 files
    fall_dir = "test_videos/falls"
    for filename in os.listdir(fall_dir):
        if filename.endswith((".mp4")):
            correct = test_video(os.path.join(fall_dir, filename), "fall")
            results["total"] += 1
            if correct:
                results["correct"] += 1

    # Test non-fall videos - only works on mp4 files
    no_fall_dir = "test_videos/no_falls"
    for filename in os.listdir(no_fall_dir):
        if filename.endswith((".mp4")):
            correct = test_video(os.path.join(no_fall_dir, filename), "no_fall")
            results["total"] += 1
            if correct:
                results["correct"] += 1

    # Print summary
    accuracy = (results["correct"] / results["total"]) * 100 if results["total"] > 0 else 0
    print(f"\n--- Results ---")
    print(f"Correct: {results['correct']} / {results['total']}")
    print(f"Accuracy: {accuracy:.1f}%")

if __name__ == "__main__":
    run_all_tests()
