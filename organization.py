import os
import time
import shutil
from datetime import datetime

# DEFINE DIRECTORIES
script_dir = os.path.dirname(os.path.abspath(__file__))
archived_dir = os.path.join(script_dir, "archived_falls")
os.makedirs(archived_dir, exist_ok=True)

# HELPER: AUDIT LOG
def log_event(filename, action):
    log_path = os.path.join(script_dir, "event_log.txt")
    with open(log_path, "a") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"{timestamp} | File: {filename} | Action: {action}\n")

# PROCESS VIDEO (ARCHIVE OR DELETE)
def manage_video(file_path, video_name, is_fall):
    if is_fall:
        dest_path = os.path.join(archived_dir, video_name)
        shutil.move(file_path, dest_path)
        log_event(video_name, "ARCHIVED (FALL DETECTED)")
        return "Archived"
    else:
        os.remove(file_path)
        log_event(video_name, "DELETED (NO FALL)")
        return "Deleted"

# CLEANUP: REMOVE FILES OLDER THAN 24 HOURS
def cleanup_old_files(folder_list):
    one_day_in_seconds = 86400
    current_time = time.time()
    
    for folder in folder_list:
        if os.path.exists(folder):
            for video in os.listdir(folder):
                if video.endswith(".mp4"):
                    file_path = os.path.join(folder, video)
                    # Get file age
                    file_age = current_time - os.path.getmtime(file_path)
                    
                    if file_age > one_day_in_seconds:
                        os.remove(file_path)
                        log_event(video, "DELETED (EXPIRED > 24H)")
                        print(f"Cleaned up expired file: {video}")
                        