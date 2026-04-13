# Controls system
# Last edited by: Alianna
# Last edit date: Mon Apr 13 2026
import os
import ai_fall_detection
from notification import send_notif
import atexit
import organization
import time
import threading
import recording_live as recorder_module

# Get newest email input
def get_email():
    """Read latest email from file"""
    if os.path.exists("email.txt"):
        with open("email.txt", "r") as f:
            return f.read().strip()
    return None

# Run fall detection
def run_admin(email=None, stop_flag=None):
    print("[ADMIN] Started")

    os.makedirs("raw_recordings", exist_ok=True)

    # SAFE PATH for recording script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    recorder_path = os.path.join(script_dir, "recording_live.py")

    # Start recording system
    recorder_module.reset_state()
    recorder_module.caretaker_email = email

    threads = [
        threading.Thread(target=recorder_module.capture_frames, daemon=True),
        threading.Thread(target=recorder_module.inference_loop, daemon=True),
        threading.Thread(target=recorder_module.save_event_video, daemon=True),
    ]
    for t in threads:
        t.start()

    folder_path = os.path.join(script_dir, "raw_recordings")

    archived_dir = os.path.join(script_dir, "archived_falls")
    os.makedirs(archived_dir, exist_ok=True)

    atexit.register(organization.cleanup_old_files, [folder_path, archived_dir])

    processed = set()

    print("[ADMIN] Watching for videos...")

    try:
        while True:
            # If  get stop condition from UI then stop
            if stop_flag and stop_flag.value:
                print("[ADMIN] Stopping admin...")
                break

            try:
                # Always get newest email
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

                        processed.add(video)

                time.sleep(2)  # prevent CPU overload

            except Exception as e:
                print("[ADMIN ERROR]", e)
                time.sleep(2)

    finally:
        # Clean up
        print("[ADMIN] Cleaning up...")
        recorder_module.stop_flag.set()
        recorder_module.fall_event.set()  # unblock save thread
        print("[ADMIN] Fully stopped")
