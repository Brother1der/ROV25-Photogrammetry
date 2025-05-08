from moviepy.editor import VideoFileClip
import os
import subprocess # possibly starts a vbs file
import keyboard
import pyautogui
import cv2
import numpy as n2
import time
import datetime

#could replace entire system with automated screenshots
resolution = (1920, 1080)
codec = cv2.VideoWriter_fourcc(*'mp4v')
fps = 30.0 # fps of file
output_path = 'path/to/your/directory/output.mp4' # Specify the output path
out = cv2.VideoWriter(output_path, codec, fps, resolution)
imageDirectory = 'path/to/your/directory/images' # Specify the output path for images

def video_capture_loop(seconds):
    start_time = time.time()
    while (time.time() - start_time) < seconds:
           img = pyautogui.screenshot()
    frame = np.array(img) # Screenshot to numpy array
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # Convert from BGR to RGB
    out.write(frame) # Writes to output file

def start_hotkey(): # Creates the hotkey's function
    print("Hotkey pressed")
    video_capture_loop(30) # Calls video capture loops function
    extract_frames(video, imageDirectory) # Calls extraction function

def extract_frames(video, imageDirectory):
    if not os.path.exists(imageDirectory):
        os.makedirs(imageDirectory)

    frame_rate = int(video.get(cv2.CAP_PROP_FPS))  # Get FPS from video
    num_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))  # Get total frame count
s   
    for i in range(num_frames):
        if i % 5 == 0:  # Save every 5 frames
            t = i / frame_rate
            frame_filename = f"{int(t*frame_rate)}.png"
            imagepath = os.path.join(imageDirectory, frame_filename)
            video.save_frame(imagepath, t)
            print(f"Saved frame at {t} seconds: {imagepath}")
# Run VBS file
#subprocess.run(["cd", "C:\Windows\Scripts"], shell=True)
#subprocess.run(["cscript scriptname.vbs"], shell=True)

# Create the VideoFileClip object
video = VideoFileClip(videoFile)

# Creates the hotkey
keyboard.add_hotkey('ctrl+shift+a', start_hotkey)

keyboard.wait('esc')  # Wait for the 'esc' key to be pressed to exit the program

# Close the video clip to release resources
video.close()