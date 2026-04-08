# Last edited by: Alianna
# Last updated date: Tue April 7 2026
import subprocess
import platform
import re
import os
import time
from datetime import datetime
import cv2
import threading
from collections import deque
from ai_fall_detection import detect_fall_from_frame

# Settings
FRAME_BUFFER_SIZE = 150   # ~5 seconds @ 30 FPS
WINDOW_SIZE = 30          # ~1 second of frames for detection
DETECTION_HISTORY = 5
DETECTION_THRESHOLD = 3
POST_EVENT_SECONDS = 3
COOLDOWN = 10

# Shared State
frame_buffer = deque(maxlen=FRAME_BUFFER_SIZE)
detection_buffer = deque(maxlen=DETECTION_HISTORY)
stop_flag = threading.Event()

lock = threading.Lock()
fall_event = threading.Event()

last_event_time = 0

def reset_state():
    frame_buffer.clear()
    detection_buffer.clear()
    stop_flag.clear()
    fall_event.clear()

# Frame Capture Thread
def capture_frames():
    cap = cv2.VideoCapture(0)
    while not stop_flag.is_set():
      while True:
         ret, frame = cap.read()
         if not ret:
               continue

         frame = cv2.resize(frame, (320, 240))  # important for Pi performance

         with lock:
               frame_buffer.append((time.time(), frame))
    
    # clean up when stop_flag is set
    cap.release()


# Inference Thread
def inference_loop():
    global last_event_time
    while not stop_flag.is_set():
        time.sleep(0.3)  # don't run every frame

        with lock:
            if len(frame_buffer) < WINDOW_SIZE:
                continue

            window = list(frame_buffer)[-WINDOW_SIZE:]
            frames = [f[1] for f in window]

        # Run detection on last frame (fast) OR whole window (better)
        fall_detected = detect_fall_from_frame(frames[-1])

        detection_buffer.append(1 if fall_detected else 0)

        if sum(detection_buffer) >= DETECTION_THRESHOLD:
            if time.time() - last_event_time > COOLDOWN:
                print("FALL DETECTED")
                fall_event.set()
                last_event_time = time.time()


# Save Video Thread
def save_event_video():
   while not stop_flag.is_set():
        fall_event.wait(timeout=1.0)  # timeout lets it check stop_flag regularly

        if not fall_event.is_set():
            continue  # timed out, loop back and check stop_flag

        print("Saving fall clip...")

        with lock:
            pre_frames = list(frame_buffer)

        post_frames = []
        start = time.time()

        while time.time() - start < POST_EVENT_SECONDS:
            with lock:
                if frame_buffer:
                    post_frames.append(frame_buffer[-1])
            time.sleep(0.03)

        all_frames = pre_frames + post_frames
        write_video(all_frames)
        fall_event.clear()


def write_video(frames):
    if not frames:
        return

    height, width, _ = frames[0][1].shape

    save_dir = "archived_falls"
    os.makedirs(save_dir, exist_ok=True)

    filename = os.path.join(save_dir, f"fall_{int(time.time())}.avi")

    out = cv2.VideoWriter(
        filename,
        cv2.VideoWriter_fourcc(*'XVID'),
        20,
        (width, height)
    )

    for _, frame in frames:
        out.write(frame)

    out.release()
    print(f"Saved: {filename}")


# Main
if __name__ == "__main__":
    threads = [
        threading.Thread(target=capture_frames, daemon=True),
        threading.Thread(target=inference_loop, daemon=True),
        threading.Thread(target=save_event_video, daemon=True),
    ]

    for t in threads:
        t.start()

    while True:
        time.sleep(1)
