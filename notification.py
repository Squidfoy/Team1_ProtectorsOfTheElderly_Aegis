# Here you send out the notification to the right emails that admin.py gives
# Last edited by: Julia
# Last updated date: Mon Mar 9 2026
import os


# Pranaya down here you can set up the program to send out real emails *************************************


def send_notif(email, video_file_name):
    # Just to check if it got the info/demo test !---#############################################
    print("Fall Alert sent to: ", email)
    # Later get camera name from admin, for now webcam is placeholder name !---#############################################
    camera_name = "webcam"
    date, ext = os.path.splitext(video_file_name)
    message = "Fall detected from {} at {}".format(camera_name, date)
    print("Message sent: ", message, "\n")


    return True
