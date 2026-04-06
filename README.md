# Aegis
Aegis the AI Based Fall Detection System is a privacy focused, camera based fall detection system designed for elderly individuals living alone. It uses AI pose estimation to passively monitor for falls and instantly notifies a designated caretaker, no wearables required.

## Table of Contents
- [Features](#features)
- [How It Works](#how-it-works)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Camera Placement Guidelines](#camera-placement-guidelines)
- [Known Limitations](#known-limitations)
- [Privacy](#privacy)
- [Team](#team)
- [Licenses](#licenses)

---

## Features
- Passive fall detection using standard security cameras: no wearables needed
- Realtime pose estimation using YOLO11
- Instant caretaker notification via email when a fall is detected
- Fully local processing: no cloud storage, no subscription fees
- Minimal data retention: only timestamp and camera location are saved
- Touch screen, keyboard and mouse compatible UI

---

## How It Works
Aegis uses a two stage AI pipeline:

1. **Human Detection**: the system first checks whether a person is present in the camera frame. If no person is detected, the fall detection pipeline stays dormant to conserve energy.
2. **Fall Detection**: once a person is detected, Aegis monitors their posture in real time using skeletal keypoint analysis. It looks for indicators of a fall including:
   - Torso becoming horizontal
   - Hips dropping suddenly toward the floor
   - Bounding box shifting from tall/narrow to wide/short
   - Sudden increase in bounding box size (toward-camera falls)

When a fall is confirmed across multiple consecutive frames, a notification is sent to the caretaker with the timestamp and camera location. No video or images are transmitted.

---

## Requirements

### Hardware
- Raspberry Pi 5 
- Raspberry Pi 5 AI HAT +2
- Compatible USB camera (standard wall or corner mount)
- MicroSD card and reader
- Power cables for Raspberry Pi (USBC)
- MicroHDMI to HDMI for setup
- Monitor o

### Software
- Python 3.10 or 3.11
- The following Python packages:
```
Ultralytics
Opencv-python
Numpy
Tkinter
```
Install them with:
```bash
pip install ultralytics opencv-python numpy
```

---

## Installation

1. Clone this repository:
```bash
git clone https://github.com/your-username/aegis.git
cd aegis
```

2. Install dependencies:
```bash
pip install ultralytics opencv-python numpy
```
Installing FFmpeg onto Raspberry Pi or Linux:
```bash
sudo apt update
sudo upgrade -y
sudo apt install ffmpeg -y
ffmpeg -version
```
When you see ffmpeg version info you're done.
To install it on Windows follow this [Youtube Video Link](https://youtu.be/SG1Fc5QB8RE)

3. On first run, the YOLO11 model will download automatically.

4. Set up your caretaker notification email in the configuration file (instructions coming in a future update).

---

## Usage

### Test on your webcam
```bash
python pose_test.py
```

### Test on video files
Place fall videos in `test_videos/falls/` and non-fall videos in `test_videos/no_falls/`, then run:
```bash
python test_on_video.py
```
This will output per-video results and a full metrics summary including accuracy, precision, recall, F1 score, and false positive/negative rates.

---

## Camera Placement Guidelines

Proper camera placement is critical for accurate fall detection. Please follow these guidelines:

- **Mount the camera at a 45 degree angle** from a wall or corner, roughly 6-8 feet off the ground. This gives the best view of the full body.
- **Do not mount the camera on the ceiling.** A top down view makes everyone appear horizontal and will cause constant false positives.
- **Do not mount the camera directly facing where the person will walk toward it.** Falls toward the camera are harder to detect than side-on falls.
- **Ensure the camera has a clear, unobstructed view** of the monitored area. Objects blocking the frame will reduce detection accuracy.
- **Avoid placing the camera behind glass** reflections and distortion affect detection quality.
- **Ensure adequate lighting.** The system works best in well lit environments. Avoid placing the camera where it will be looking directly into a bright light source.
- **Test the camera feed** before relying on the system by running `pose_test.py` and confirming the skeleton overlay appears correctly on a person standing in the monitored area.

---

## Known Limitations

Aegis is designed for practical home use but has several known limitations that users and caretakers should be aware of:

- **Falls toward the camera** are harder to detect than side-on falls. The system uses bounding box analysis to partially address this, but accuracy is lower for this fall direction. Avoid placing the camera in a position where a person would fall directly toward it.
- **Ceiling mounted cameras** are not supported. The top down perspective breaks the pose-based detection logic entirely.
- **Occlusion**: if the person's body is partially blocked by furniture or other objects, keypoint detection may fail and falls could be missed.
- **Slow, deliberate movements to the floor** (such as someone intentionally lying down or getting on the floor to look under furniture) may occasionally trigger a false positive. The system uses posture history to reduce this, but edge cases remain.
- **Single person monitoring**: the system is optimized for monitoring one person at a time. Accuracy may decrease in scenes with multiple people.
- **Lighting sensitivity**: very dark environments or scenes with dramatic lighting changes (e.g. flickering lights) may reduce detection accuracy.
- **Camera angle sensitivity**: the system is optimized for standard wall or corner-mounted cameras. Unusual angles may affect accuracy.
- **Falls where the person's back is fully facing the camera** may result in missed detections due to keypoint occlusion.

---

## Privacy

Aegis is designed with user privacy as a core principle:

- All processing happens in the device **locally**: no video is ever sent to the cloud.
- **No video footage is stored** after processing. Only the timestamp and camera location of a detected fall are saved.
- Caretaker notifications contain only the time and location of the event, no images or video clips are included.
- All data is deleted once the notification has been sent or if no fall is detected.

## Team

Aegis was developed by students at the **University of Missouri** as part of the INFOTC-4970W Senior Capstone Design course.

| Name | Role |
|------|------|
| Alianna Card | AI model implementation and optimization |
| Julia Albay | Baseline system architecture |
| Sania Akter Sohana | Backend video organization |
| Pranaya Bollu | |

**Mentor:** Michael Tompkins

---

## Licenses
**YOLO11** is used for pose estimation and is available for private use under the [AGPL-3.0 License](https://www.gnu.org/licenses/agpl-3.0.html). If you plan to use Aegis in a commercial context, a separate Ultralytics commercial license would be required.

**UR Fall Detection Dataset**: the test videos used during development are from the UR Fall Detection Dataset:

> Bogdan Kwolek, Michal Kepski, "Human fall detection on embedded platform using depth maps and wireless accelerometer," *Computer Methods and Programs in Biomedicine*, Volume 117, Issue 3, December 2014, Pages 489-501, ISSN 0169-2607. [Dataset Link](https://fenix.ur.edu.pl/mkepski/ds/uf.html)

This dataset is licensed under a [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-nc-sa/4.0/) and is intended for non-commercial academic use only.

---
