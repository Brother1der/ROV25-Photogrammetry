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



def create_3D_reconstruction(output_folder):
    '''
    don't worry gemini will work this time I swear.
    # 1. Load the image file using Pillow
    image_path = 'path/to/your/image.jpg'  # Replace with your image file path
    img_pil = Image.open(image_path).convert('RGB') # Load as RGB
    
    # 2. (Optional) Convert to grayscale if needed for SIFT extraction
    # SIFT feature extraction in pycolmap often expects grayscale images.
    img_grayscale_pil = ImageOps.grayscale(img_pil)
    
    # 3. Convert the Pillow image object to a NumPy array
    # Ensure the data type is float and normalized to [0, 1] if required by the pycolmap function
    img_np = np.array(img_grayscale_pil).astype(np.float32) / 255.0
    
    # Now, 'img_np' is a NumPy array representing your image, ready for pycolmap functions
    # For example, to extract SIFT features:
    sift = pycolmap.Sift()
    keypoints, descriptors = sift.extract(img_np)
    
    print(f"Image shape: {img_np.shape}")
    print(f"Number of keypoints: {len(keypoints)}")
    '''

    # Sparse Reconstruction
    mvs_path = output_folder + "\\" + "mvs"
    database_path = output_folder + "\\" + "database.db"

    pycolmap.extract_features(database_path, imageDirectory)
    pycolmap.match_exhaustive(database_path)
    maps = pycolmap.incremental_mapping(database_path, imageDirectory, output_folder)
    print(maps)
    maps[0].write(output_folder)
    maps[0].export_PLY(output_folder + "\\sparse.ply")

    # dense reconstruction
    pycolmap.undistort_images(mvs_path, output_folder, imageDirectory) #Eventually will be updated with camera.
    pycolmap.patch_match_stereo(mvs_path) 
    print("0")
    pycolmap.stereo_fusion(mvs_path + "\\" + "dense.ply", mvs_path)

# Gets y-midpoint (index 0) and total height (index 1)
def get_vertical_details(reconstruction):
    list_of_points = reconstruction.points3D.items()
    list_of_y_values = list_of_points.xyz[:,1]
    return [((max(list_of_y_values) + min(list_of_y_values)) / 2), abs(max(list_of_y_values) - min(list_of_y_values))]

# Gets points within a certain y-boundary from the midpoint. Precision denotes how much of the height will be factored in for using points. (Ex. 0.1 is 0.1 of the total height.) Recommend using precision that is < 0.2 and > 0.
# Uses these points to get the dimensions of the coral prop for resizing.
# Returns the larger of the two dimensions (index 0) and the lesser (index 2). Assumes that boundary used to scale is the longer of the two.
def get_reconstruction_resize_dimensions(reconstruction, precision):
    list_of_points = reconstruction.points3D.items()
    y_details = get_vertical_details(reconstruction)
    y_height = y_details[1] * precision
    y_mid = y_details[0] - (y_details[1] * 0.1)
    filtered_points = []
    for point3D in list_of_points.items():
        if point3D.xyz[1] >= y_mid + y_height and point3D.xyz[1] <= y_mid - y_height:
            filtered_points.append(point3D)
    list_of_x_values = filtered_points.xyz[:,0]
    list_of_z_values = filtered_points.xyz[:,2]
    x_total = abs(max(list_of_x_values) - min(list_of_x_values))
    z_total = abs(max(list_of_z_values) - min(list_of_z_values))
    return (max(x_total, z_total), min(x_total, z_total))

def resize_dimensions(reconstruction, given_dimension, reconstruction_dimensions):
    transform_instructions = pycolmap.Sim3d()
    transform_instructions.scale = reconstruction_dimensions[0] / given_dimension
    reconstruction.transform(transform_instructions)


# Creates the hotkey
    keyboard.add_hotkey('ctrl+shift+a', start_hotkey)

    wait = keyboard.wait('esc')  # Wait for the 'esc' key to be pressed
    sys.exit(0)  # Exit the script











