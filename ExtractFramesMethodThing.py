from moviepy.editor import VideoFileClip
import os

print('Enter Video File:')
videoFile = input()
print('Enter Directory:')
imageDirectory = input()

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

# Call the function
extract_frames(video, imageDirectory)

# Close the video clip to release resources
video.close()