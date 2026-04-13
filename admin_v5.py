# Controls system
# Last edited by: Julia
# Last edit date: Sun Apr 12 2026
import subprocess
import os
import ai_fall_detection
from notification import send_notif
import atexit
import organization
import time

# Get newest email input
def get_email():
    """Read latest email from file"""
    if os.path.exists("email.txt"):
        with open("email.txt", "r") as f:
            return f.read().strip()
    return None

# Run fall detection
def run_admin(email=None):
    print("[ADMIN] Started")

    os.makedirs("raw_recordings", exist_ok=True)

    # Start recording system
    subprocess.Popen(["python", "recording_live.py"])

    script_dir = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(script_dir, "raw_recordings")

    archived_dir = os.path.join(script_dir, "archived_falls")
    os.makedirs(archived_dir, exist_ok=True)

    atexit.register(organization.cleanup_old_files, [folder_path, archived_dir])

    if not os.path.exists(folder_path):
        return

    print("[ADMIN] Watching for videos...")

    processed = set()

    while True:
        try:
            # Always gets newest email input
            current_email = get_email()

            for video in os.listdir(folder_path):
                if video.endswith(".mp4") and video not in processed:

                    file_path = os.path.join(folder_path, video)

                    print(f"[ADMIN] Processing {video}")

                    result = ai_fall_detection.fall_check(folder_path, video)
                    print(result)

                    if current_email:
                        send_notif(current_email, video)
                        print(f"[ADMIN] Notification sent to {current_email}")
                    else:
                        print("[ADMIN] No email set")

                    print("------------------------")

                    processed.add(video)

            time.sleep(2)  # prevent CPU overload

        except Exception as e:
            print("[ADMIN ERROR]", e)
            time.sleep(2)
