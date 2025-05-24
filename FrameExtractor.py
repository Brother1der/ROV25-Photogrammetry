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

def get_raw_string_from_file(file_path):
    """
    Reads a text file and returns its content as a raw string.

    Args:
        file_path (str): The path to the text file.

    Returns:
        str: The content of the file as a raw string.
             Returns None if the file cannot be opened.
    """
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            raw_content = repr(content)
            return raw_content
    except FileNotFoundError:
        print(f"Error: File not found at path: {file_path}")
        return None
    except Exception as e:
         print(f"An error occurred: {e}")
         return None

# Create the VideoFileClip object
video = VideoFileClip(videoFile)

# Creates the hotkey
keyboard.add_hotkey('ctrl+shift+a', start_hotkey)

# Run VBS file
subprocess.run(["cd", "C:\Windows\Scripts"], shell=True)
subprocess.run(["cscript scriptname.vbs"], shell=True)

keyboard.wait('esc')  # Wait for the 'esc' key to be pressed to exit the program

# Close the video clip to release resources
video.close()
