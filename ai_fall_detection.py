# We'll use the test_on_dataset.py's code to do prototype for midterm
# Than later use pose_test.py after we get live feed working
# Just need to modify it for admin.py
# For now I'll use this place holder code to test
# Last edited by: Julia
# Last updated date: Mon Mar 9 2026
import os


# Use the Ai fall model to look at video
# Send result back to admin.py as boolean value
def fall_check(folder_dir, video_file_name):
    # Get the video location info
    file_path = os.path.join(folder_dir, video_file_name)
    print("At: ", file_path)
    print("Checking for fall in video: ", video_file_name)


    # Alianna you can out the ai model code here**************************************
    # Use the same test_on_dataset.py code
    # But instead of the dataset videos just use video_file_name or file_path


    # *****************************************************************


    # Than send result
    fall = False
    return False


