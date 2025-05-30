from moviepy.editor import VideoFileClip
import os
import time
import sys
import subprocess
import keyboard
import glob
from pymavlink import mavutil

dir_path = r'replace_with_dir'
imageDirectory = r'replace_with_dir'
connection = mavutil.mavlink_connection('udpin:0.0.0.0.14550') #example pin idk about mavutil
videoFile = None

def start_hotkey(): # Creates the hotkey's function
    print("Hotkey pressed")
    connect_to_mavlink()  # Connect to MAVLink
    time.sleep(1)  # Wait for connection to establish
    start_video_capture()  # Start video capture
    time.sleep(1)  # Wait for 1 second before extracting frames
    get_latest_file(dir_path)  # Get the latest video file
    videoFile = r"{}".format(get_latest_file(dir_path))
    video = VideoFileClip(videoFile) # Load the video files
    extract_frames(video, imageDirectory) # Calls extraction function
    time.sleep(1)
    os.chdir("C:\\Windows\\Scripts")
    subprocess.run(["cscript", "scriptname.vbs"], shell=True)

def extract_frames(video, imageDirectory):
    if not os.path.exists(imageDirectory):
        os.makedirs(imageDirectory)

    frame_rate = video.fps
    num_frames = int(video.fps * video.duration)
   
    for i in range(num_frames):
        if i % 5 == 0:  # Save every 5 frames
            t = i / frame_rate
            frame_filename = f"{int(t*frame_rate)}.png"
            imagepath = os.path.join(imageDirectory, frame_filename)
            video.save_frame(imagepath, t)
            print(f"Saved frame at {t} seconds: {imagepath}")
    video.close()

def get_latest_file(dir_path):
    """
    Gets the latest file in a directory based on modification time.

    Args:
        dir_path (str): The path to the directory.

    Returns:
        str: The path to the latest file, or None if the directory is empty or an error occurs.
    """
    try:
        list_of_files = glob.glob(os.path.join(dir_path, '*.mp4'))  # Get list of all mp4 files in directory
        if not list_of_files:
            return None  # Return None if directory is empty
        latest_file = max(list_of_files, key=os.path.getmtime)  # Get file with the latest modification time
        return latest_file
    except OSError as e:
         print(f"Error accessing directory: {e}")
         return None

def connect_to_mavlink():
    try:
        connection.wait_heartbeat()
        print("MAVLink connection established")
    except Exception as e:
        print(f"Failed to connect to MAVLink: {e}")

def start_video_capture():
    msg = connection.message_factory.command_long_encode(
        0, 0,  # target_system, target_component
        mavutil.mavlink.MAV_CMD_VIDEO_START_CAPTURE,  # command
        0, 0, 0, 0, 0, 0, 0,
        # param1, param2, param3, param4, param5, param6, param7
        print("Sent MAV_CMD_VIDEO_START_CAPTURE command")
    )
    msg2 = connection.message_factory.command_long_encode(
        0, 0,
        mavutil.mavlink.MAV_CMD_VIDEO_STOP_CAPTURE,  # command to stop video capture
        0, 0, 0, 0, 0, 0, 0,
        print("Sent MAV_CMD_VIDEO_STOP_CAPTURE command")
    )
    connection.send_mavlink(msg)
    time.sleep(10)
    connection.send_mavlink(msg2)
    connection.close()




# Creates the hotkey
keyboard.add_hotkey('ctrl+shift+a', start_hotkey)

wait = keyboard.wait('esc')  # Wait for the 'esc' key to be pressed
sys.exit(0)  # Exit the script
