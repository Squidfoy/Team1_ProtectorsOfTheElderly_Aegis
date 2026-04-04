# Control the whole project from this admin file
# Last edited by: Julia
# Last updated date: Fri Apr 4 2026
import subprocess # To run other python files/system commands
import os # Give access to video files, folders, paths
import ai_fall_detection # Process the videos for fall
from notification import send_notif # To send notification
import atexit # To clean up videos automatically
import organization # organize videos

# The log names for the termial and video activity to be used in UI
LOG_FILE = "admin_log.txt"
VIDEO_LIST_FILE = "video_list.txt"


# Log the terminal for UI
def log(text):
    print(text)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(text + "\n")

# Log the video list file
def update_video_list_file(folder_path):
    videos = [f for f in os.listdir(folder_path) if f.endswith(".mp4")]

    with open(VIDEO_LIST_FILE, "w", encoding="utf-8") as f:
        if not videos:
            f.write("No videos found.\n")
        else:
            for vid in videos:
                f.write(vid + "\n")

# Main function to run everything
def run_admin(email):
    # Clear logs at start
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write(f"The email user entered: {email}\n")
        f.write("---------------------------------------------------\n")

    with open(VIDEO_LIST_FILE, "w", encoding="utf-8") as f:
        f.write("Loading videos...\n")

    # Make sure folders exist
    make_folder = "raw_recordings"
    os.makedirs(make_folder, exist_ok=True)
    log(f"Make sure the video folder exists: {make_folder}")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(script_dir, "raw_recordings")

    archived_dir = os.path.join(script_dir, "archived_falls")
    os.makedirs(archived_dir, exist_ok=True)

    # Cleanup videos folder on exit
    atexit.register(organization.cleanup_old_files, [folder_path, archived_dir])

    # Start recording
    log("Starting recording_live.py ...")
    try:
        subprocess.run(["python", "recording_live.py"], check=True)
        log("Recording finished.")
    except subprocess.CalledProcessError as e:
        log(f"Error running recording_live.py: {e}")

    # Update list after recording
    update_video_list_file(folder_path)

    # Process the videos
    videos = os.listdir(folder_path)

    if not videos:
        log("No videos found in raw_recordings.")

    for video in videos:
        if not video.endswith(".mp4"):
            log(f"{video} is not a mp4 file, skipping.")
            continue

        file_path = os.path.join(folder_path, video)
        log(f"Processing {video} ...")

        # Run AI fall detection
        try:
            check_result = ai_fall_detection.fall_check(folder_path, video)
            log(f"Result: {check_result}")
            is_fall = "FALL DETECTED" in check_result
        except Exception as e:
            log(f"Error processing {video}: {e}")
            continue

        # Manage video (move/delete)
        try:
            organization.manage_video(file_path, video, is_fall)
            log(f"Handled video: {video}")
        except Exception as e:
            log(f"Error managing {video}: {e}")

        # Update video list after change
        update_video_list_file(folder_path)

        # Send notification
        try:
            if is_fall:
                send_notif(email, video)
                log(f"Notification sent for {video}")
        except Exception as e:
            log(f"Error sending notification: {e}")

        log("---------------------------------------------------")

    # Let user know program is done
    log("Finished detecting for falls.")
    log("You may exit.")
    
