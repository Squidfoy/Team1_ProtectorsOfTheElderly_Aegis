# Control the whole project from this admin file
# Last edited by: Julia
# Last updated date: Mon Mar 9 2026
import subprocess
import os
import ai_fall_detection
from notification import send_notif

# Create the raw_recordings empty folder to store the videos in
# Since github doesn't allow empty folder uploads
make_folder = "raw_recordings"
os.makedirs(make_folder, exist_ok=True)

# Get the contact info of whoever gets the notifications alert
# We can make this more polished with UI later !---#############################################
done_email_input = False
while not done_email_input:
    print("Who's email address would you like the fall alert notifications to be sent to?")
    print("Enter the email address here: ")
    email = input()
    print("\nIs ", email, " the correct email? Enter y for YES, n for NO: ")
    confirmation = input()
    if confirmation == "y":
        done_email_input = True
    else:
        done_email_input = False
print("--------------------------------------------------------------------------------------")




# Later be able to send live camera feed to other py files !---#############################################
# For now its saved recordings from raw_recordings folder using recording_live.py
subprocess.run(["python", "recording_live.py"])


# Get the path to the raw recordings
script_dir = os.path.dirname(os.path.abspath(__file__))
folder_path = os.path.join(script_dir, "raw_recordings")


# Now list all the files in folder
videos = os.listdir(folder_path)


for video in videos:
    # Get the video file name
    video_file_name = video
    # Make sure its a mp4 before using model
    if video.endswith(".mp4"):
        # Than use ai model here to check for fall using the video file name
        check_result = ai_fall_detection.fall_check(folder_path, video_file_name)
        # Print result
        print(check_result, "\n")
        # Maybe add file renaming here/Flag fall event/Moving it to fall_detected folder !---#############################################


        # Than send out notification if fall is detected
        print("---------------------------------------------------------------------")
        send_notif(email, video_file_name)
    else:
        print(video, " is not a mp4 file.")


# Maybe build a loop for those two pys files to run for certain amount of time !---#############################################
# But we'll do that after midterm maybe !---#############################################
