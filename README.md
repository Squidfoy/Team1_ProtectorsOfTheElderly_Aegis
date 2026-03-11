# Team1_ProtectorsOfTheElderly_Aegis

To begin, ensure you have python installed on your system. Also insure ffmpeg is installed or the detection will not work.

Then install the required packages by running pip install ultralytics opencv-python in the terminal. ultralytics is the package that contains YOLOv8 and opencv-pyton handles video processing. 

pose_test.py currently works with the users webcam and test_on_dataset.py tests dataset videos.

The fall detection works with YOLOv8 with is avalible for private use under the AGPL-3.0 license

Note: for the fall videos here I have used the UR fall detection dataset:
Bogdan Kwolek, Michal Kepski, Human fall detection on embedded platform using depth maps and wireless accelerometer, Computer Methods and Programs in Biomedicine, Volume 117, Issue 3, December 2014, Pages 489-501, ISSN 0169-2607 [Link]

This work is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License and is intended for non-commercial academic use. 

Link to the dataset: https://fenix.ur.edu.pl/mkepski/ds/uf.html

Note about camera placement: This fall detection works from side views and not birds-eye so cameras installed in the ceiling will not work. This is designed for wall/corner cameras.
