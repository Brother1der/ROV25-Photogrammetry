from moviepy.editor import VideoFileClip
import os
import keyboard
import pyautogui
import cv2
import numpy as np
import time

# Configuration
resolution = (1920, 1080)
codec = cv2.VideoWriter_fourcc(*'mp4v')
fps = 30.0  # FPS of the output file
output_path = 'path/to/your/directory/output.mp4'  # Specify the output path
imageDirectory = 'path/to/your/directory/images'  # Specify the output path for images

# Initialize VideoWriter
out = cv2.VideoWriter(output_path, codec, fps, resolution)

def video_capture_loop(seconds):
    start_time = time.time()
    while (time.time() - start_time) < seconds:
        img = pyautogui.screenshot()
        frame = np.array(img)  # Screenshot to numpy array
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert from BGR to RGB
        out.write(frame)  # Write frame to output file
    print("Video capture completed.")

def extract_frames(video_path, imageDirectory):
    if not os.path.exists(imageDirectory):
        os.makedirs(imageDirectory)

    video = cv2.VideoCapture(video_path)
    try:
        frame_rate = int(video.get(cv2.CAP_PROP_FPS))  # Get FPS from video
        num_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))  # Get total frame count

        for i in range(num_frames):
            ret, frame = video.read()
            if not ret:
                break
            if i % 5 == 0:  # Save every 5th frame
                frame_filename = f"{i}.png"
                imagepath = os.path.join(imageDirectory, frame_filename)
                cv2.imwrite(imagepath, frame)  # Save frame as an image
                print(f"Saved frame {i}: {imagepath}")
    finally:
        video.release()  # Release video resource
    print("Frame extraction completed.")

def start_hotkey():
    """Hotkey function to start video capture and frame extraction."""
    print("Hotkey pressed")
    video_capture_loop(30)  # Capture video for 30 seconds
    out.release()  # Release the VideoWriter
    extract_frames(output_path, imageDirectory)  # Extract frames from the captured video

# Set up the hotkey
keyboard.add_hotkey('ctrl+shift+a', start_hotkey)

# Wait for the 'esc' key to exit the program
print("Press 'Ctrl+Shift+A' to start, or 'Esc' to exit.")
keyboard.wait('esc')

# Release resources
out.release()
print("Program exited.")