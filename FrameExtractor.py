from moviepy.editor import VideoFileClip
import os
import subprocess #possibly starts a vbs file
import keyboard
from pymavlink import mavutil

videoFile = r'replace_with_dir'
imageDirectory = r'replace_with_dir'
connection = mavutil.mavlink_connection('udpin:0.0.0.0.14550') #example pin idk about mavutil

def start_hotkey(): # Creates the hotkey's function
    print("Hotkey pressed")
    connect_to_mavlink()  # Connect to MAVLink
    time.sleep(1)  # Wait for connection to establish
    start_video_capture()  # Start video capture
    time.sleep(1)  # Wait for 1 second before extracting frames
    extract_frames(video, imageDirectory) # Calls extraction function

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
        0, 0, 0, 0, 0, 0, 0  # param1 param2, param3, param4, param5, param6, param7
        print("Sent MAV_CMD_VIDEO_START_CAPTURE command")
        time.sleep(10) # pause prog for 10 sec
        mavutil.mavlink.MAV_CMD_VIDEO_STOP_CAPTURE  # command to stop video capture
        0, 0, 0, 0, 0, 0, 0  # param1, param2, param3, param4, param5, param6, param7
        print("Sent MAV_CMD_VIDEO_STOP_CAPTURE command")
    )
    connection.close()


# Create the VideoFileClip object
video = VideoFileClip(videoFile)

# Creates the hotkey
keyboard.add_hotkey('ctrl+shift+a', start_hotkey)

# Run VBS file
subprocess.run(["cd", "C:\Windows\Scripts"], shell=True)
subprocess.run(["cscript scriptname.vbs"], shell=True)

# Close the video clip to release resources
video.close()

sys.exit(0)  # Exit the script