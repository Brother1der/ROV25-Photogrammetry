from moviepy import VideoFileClip
import os
import time
import sys
import subprocess
import keyboard
import glob
import serial
import pycolmap
from pymavlink import mavutil
 
video_dir_path = r'replace_with_dir' #Directory of the folder that holds the videos
imageDirectory = r'replace_with_dir' #Directory of Folder with all of the images.
connection = None
try:
    connection = mavutil.mavlink_connection('192.168.2.2') #example pin idk about mavutil
except Exception as n:
    connection = None
videoFile = None

def start_hotkey(): # Creates the hotkey's function
    print("Hotkey pressed")
    connect_to_mavlink()  # Connect to MAVLink
    time.sleep(1)  # Wait for connection to establish
    start_video_capture()  # Start video capture
    time.sleep(1)  # Wait for 1 second before extracting frames
    videoFile = get_latest_file(video_dir_path)  # Get the latest video file
    videoFile = r"{}".format(videoFile) # reason we do the whole .format thingy is so that we can get the raw path of the file, saving headaches and code later
    video = VideoFileClip(videoFile) # Load the video files
    extract_frames(video, imageDirectory) # Calls extraction function
    time.sleep(5) # Wait for 5 seconds so all the frames are saved to be safe.

def extract_frames(video, imageDirectory):
    if not os.path.exists(imageDirectory):
        os.makedirs(imageDirectory)

    frame_rate = video.fps
    num_frames = int(video.fps * video.duration)
   
    for i in range(num_frames):
        if i % 5 == 0:  # WE MAY WANT TO MAKE IT TAKE ALL OF THE FRAMES FROM THE VIDEO FOR MORE ACCURATE RECONSTRUCTION.
            t = i / frame_rate
            frame_filename = f"{int(t*frame_rate)}.png"
            imagepath = os.path.join(imageDirectory, frame_filename)
            video.save_frame(imagepath, t)
            print(f"Saved frame at {t} seconds: {imagepath}")
    video.close()

def get_latest_file(dir_path):
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



def create_3D_reconstruction(width, height, output_folder):
    reconstruction = pycolmap.Reconstruction()
    cameraType = pycolmap.CameraModelId.SIMPLE_RADIAL #Most likely to be what we're going to use.
    params = [1500,960,540] # Focal length, CX, CY
    # Try to figure out what CX and CY are for ROV? Not entirely certain as to what it is. Has to do with camera specs.
    # Online sources pointed me to look at this. > https://en.wikipedia.org/wiki/Camera_resectioning
    # See what you can pry from this article if you could.
    reconstruction.add_camera(1,cameraType, width, height, params)
    #Camera ID is 1.

    # Add images to the reconstruction.
    try:
        list_of_files = glob.glob(os.path.join(imageDirectory, '*.png'))  # Get list of all image files in directory
        if not list_of_files:
            pass
        count = 1
        for n in list_of_files:
            reconstruction.add_image(count, n, 1)
            count += 1
    except OSError as e:
         print(f"Error accessing directory: {e}")
         return None
    try:
        list_of_files = glob.glob(os.path.join(imageDirectory, '*.png'))  # Get list of all image files in directory. We'll make this more efficient later.
        if not list_of_files:
            pass

        pycolmap.extract_features(output_folder, imageDirectory)
        pycolmap.match_features(output_folder)
        pycolmap.incremental_reconstruction(output_folder, output_folder)

        reconstruction = pycolmap.Reconstruction(output_folder + "/sparse") # I am sorry I totally used the google ai for this. but genuinely there is like NO documentation for this stupid library. Also I haven't tested it. (I'm not gonna test it for a decent bit, at least.)
        # Important things needed for testing: Way to figure out CX and CY for cameras. Way to figure out Focal Length as well. Known width and height (in pixels) of our images. We'll polish this out later and see if it even works, but for now, it's something.
        reconstruction.write(output_folder + "/sparse")
    except OSError as e:
         print(f"Error accessing directory: {e}")
         return None


# Creates the hotkey
keyboard.add_hotkey('ctrl+shift+a', start_hotkey)

wait = keyboard.wait('esc')  # Wait for the 'esc' key to be pressed
sys.exit(0)  # Exit the script



