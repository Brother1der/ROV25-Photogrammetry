from moviepy.editor import VideoFileClip
import os
import subprocess #possibly starts a vbs file
import keyboard

videoFile = r'replace_with_dir'
imageDirectory = r'replace_with_dir'

def start_hotkey(): # Creates the hotkey's function
    print("Hotkey pressed")
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

# Create the VideoFileClip object
video = VideoFileClip(videoFile)

# Creates the hotkey
keyboard.add_hotkey('ctrl+shift+a', start_hotkey)

keyboard.wait('esc')  # Wait for the 'esc' key to be pressed to exit the program

# Run VBS file
#subprocess.run(["cd", "C:\Windows\Scripts"], shell=True)
#subprocess.run(["cscript scriptname.vbs"], shell=True)

# Close the video clip to release resources
video.close()
