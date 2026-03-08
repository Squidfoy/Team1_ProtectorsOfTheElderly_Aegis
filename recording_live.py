# Save live video feed from camera, as mp4 by using FFmpeg
# Last edited by: Julia
# Last updated date: Sun Mar 8 2026

import subprocess
import platform
import re
import os
import time
from datetime import datetime

# Later add import values from pose_test.py, test_on_dataset.py, and admin.py here !---###################
# 
# So it can only save when needed or save file name as fall for fall detections !---###################

# Fall event flagger to put in filename
# Later change it to use pose_test.py's fall_detected boolean value !---###################
Emergency = False
if Emergency == True:
    event_name = "Fall_"
else:
    event_name = "Human_"

# Get timestamp for filename
timestamp = datetime.now().strftime("_%H-%M__%m-%d-%Y")
filename = f"{event_name}{timestamp}.mp4"

# Save it in same folder as this code to find it fast/easier for testing
# Later change it to have folder and files it creates to store and find !---###############
script_dir = os.path.dirname(os.path.abspath(__file__))
output_file = os.path.join(script_dir, filename)


# Check which Operating System its being run on (Windows, Darwin/MacOS, Linux)
# Than pick the first camera listed since that would be the webcam for testing
# Later change it to be whicher cameras are connected to admin.py !---#####################
# Later change it to be in the admin.py !---###############################################
# Later change it to work for rasberry pi !---#############################################
system = platform.system()
command = None

# Only tested the windows and it works, macos and Linux unknown !---#######################
# But linux can prob be tested in rasberry pi !---#########################################
# Windows version
if system == "Windows":
    # List available video devices
    result = subprocess.run(
        ["ffmpeg", "-list_devices", "true", "-f", "dshow", "-i", "dummy"],
        capture_output=True,
        text=True
    )

    # Extract video device names
    video_devices = re.findall(r'\[dshow @ .*?\]\s+"(.*?)"', result.stderr)
    if not video_devices:
        print("No video devices found!")
        exit()
   
    # Pick the first camera which usual would be the webcam
    camera_name = video_devices[0]
    print(f"Using camera: {camera_name}")
   
    # FFmpeg command (get video only no audio)
    command = [
        "ffmpeg",
        "-f", "dshow",
        "-i", f"video={camera_name}",
        "-vcodec", "mpeg4",
        "-q:v", "5",
        "-an",  # Disables audio
        output_file
    ]
# MacOS version
elif system == "Darwin":  # Name for macOS
    # List devices: requires avfoundation
    result = subprocess.run(
        ["ffmpeg", "-f", "avfoundation", "-list_devices", "true", "-i", ""],
        capture_output=True,
        text=True
    )

    # Pick the first camera (index 0)
    camera_index = "0"
    print("Using first available camera (index 0) on macOS")
   
    command = [
        "ffmpeg",
        "-f", "avfoundation",
        "-i", camera_index,
        "-vcodec", "mpeg4",
        "-q:v", "5",
        "-an",
        output_file
    ]
# Linux version
elif system == "Linux":
    # On Linux, the first camera is /dev/video0 most likely
    camera_device = "/dev/video0"
    print(f"Using camera device: {camera_device}")
   
    command = [
        "ffmpeg",
        "-f", "v4l2",
        "-i", camera_device,
        "-vcodec", "mpeg4",
        "-q:v", "5",
        "-an",
        output_file
    ]
# Unsupported versions
else:
    print(f"Your Operating System is not supported for this program: {system}")
    exit()


# Start recording
try:
    recorder = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    # For now its 5 seconds or 10 seconds to just test later we can change it !---#######################
    print(f"Recording video only for 5 seconds...\nSaving as: {output_file}")
    time.sleep(5)

    # stop recording by sending 'q' to stop ffmpeg
    recorder.communicate(input="q")
    print(f"Recording saved: {output_file}")


except FileNotFoundError:
    print("FFmpeg not found. Please install it.")
