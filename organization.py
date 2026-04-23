import os
import time
import shutil
from datetime import datetime

# DEFINE DIRECTORIES
script_dir = os.path.dirname(os.path.abspath(__file__))
archived_dir = os.path.join(script_dir, "archived_falls")
os.makedirs(archived_dir, exist_ok=True)

# Set to True for testing (5 min expiry), False for production (24 hr expiry)
TESTING_MODE = False

EXPIRY_LIMIT = 300 if TESTING_MODE else 86400  # seconds

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

# CLEANUP: REMOVE FILES OLDER THAN EXPIRY LIMIT
def cleanup_old_files(folder_list):
    current_time = time.time()
    expiry_label = "5 min" if TESTING_MODE else "24 hr"

    for folder in folder_list:
        if not os.path.exists(folder):
            print(f"[ORGANIZATION] Folder not found, skipping: {folder}")
            continue

        for filename in os.listdir(folder):
            # Check both .mp4 and .avi files
            if not filename.endswith((".mp4", ".avi")):
                continue

            file_path = os.path.join(folder, filename)

            try:
                file_age = current_time - os.path.getmtime(file_path)

                if file_age > EXPIRY_LIMIT:
                    os.remove(file_path)
                    log_event(filename, f"DELETED (EXPIRED > {expiry_label})")
                    print(f"[ORGANIZATION] Cleaned up expired file: {filename}")
                else:
                    remaining = EXPIRY_LIMIT - file_age
                    hours = int(remaining // 3600)
                    minutes = int((remaining % 3600) // 60)
                    print(f"[ORGANIZATION] {filename} expires in {hours}h {minutes}m")

            except Exception as e:
                print(f"[ORGANIZATION] Error processing {filename}: {e}")
                        
