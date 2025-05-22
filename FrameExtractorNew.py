import os
import subprocess
import time
import keyboard
import pyautogui

fps = 6
seconds = 5
output_dir = r"C:\Example\Screenshots"

def get_screenshots(fps, sec, output_dir):
    ss_num = 1
    start_time = time.time()
    while (time.time() - start_time) < seconds:
        if time.time() % (1/fps(ss_num)) == 0:
            screenshot = pyautogui.screenshot()
            screenshot.save(os.path.join(output_dir, f"screenshot_{int(time.time())}.png"))
            ss_num += 1