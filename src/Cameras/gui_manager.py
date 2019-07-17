import cv2
import numpy as np
import PIL.Image, PIL.ImageTk
import time
import threading

from argparse import ArgumentParser
from gui import App
from tkinter import *


# Import OpenPose and necessary libraries for OpenPose
import os
import sys
from sys import platform

dir_path = os.path.dirname(os.path.realpath(__file__))
try:
    # Windows Import
    if platform == 'win32':
        # Change variables to point to the python release folder (Release/x64 etc.)
        sys.path.append(dir_path + '/../../openpose/windows/python/openpose/Release');
        os.environ['PATH'] = os.environ['PATH'] + ';' + dir_path + '/../../openpose/windows/x64/Release;' + dir_path + '/../../openpose/windows/bin;'
        import pyopenpose as op
    else:
        # Change variables to point to the python release folder
        sys.path.append('../../openpose/unix/build/python');
        from openpose import pyopenpose as op
except ImportError as e:
    print('Error: OpenPose library could not be found. Was `BUILD_PYTHON` enabled in CMake when OpenPose was built? Is the python script in the right folder?')
    raise e


# Get video flag
parser = ArgumentParser()
parser.add_argument('--video', default='0', dest='video', type=str, help='The path to a video or number of the camera used for capture.')
video = parser.parse_args().video
try:
    video = int(video)
except ValueError:
    video = 0

# Create output directory if it does not exist
if not os.path.exists('output'):
    os.makedirs('output')


class ProcessThread(threading.Thread):
    def __init__(self, event, progress, gui):
        threading.Thread.__init__(self)
        self.stopped = event
        self.progress = progress
        self.data = gui.data
        gui.cap.release()
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.writer = cv2.VideoWriter('output/processed_output.mp4', fourcc, 30, (gui.vid_width, gui.vid_height))
        self.vid_length = len(self.data)

        # OpenPose setup
        params = dict()
        params['model_folder'] = 'openpose/models/'
        params['face'] = True
        params['hand'] = True
        self.opWrapper = op.WrapperPython()
        self.opWrapper.configure(params)
        self.opWrapper.start()
        self.datum = op.Datum()

    def run(self):
        frames_completed = 0
        while not self.stopped.isSet():
            # Process a frame from the file
            if len(self.data) == 0:
                print('Processing failed...')
                self.writer.release()
                return
            self.datum.cvInputData = self.data[frames_completed]
            self.opWrapper.emplaceAndPop([self.datum])
            self.writer.write(self.datum.cvOutputData)

            frames_completed += 1
            self.progress[0] = frames_completed / self.vid_length
            if frames_completed >= self.vid_length:
                self.stopped.set()
                print('Processing complete...')
                self.writer.release()
                return
        self.writer.release()


class GUIManager:

    def __init__(self, master, camera_source=0):
        self.current_screen = 0
        self.app = App(self, master)
        self.run_time = 15.0
        self.stop_processes = False
        self.camera_source = camera_source
        self.cap = cv2.VideoCapture(self.camera_source)
        self.vid_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.vid_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.data = []


    def start(self, time):
        self.current_screen = 1
        self.app.set_screen(self.current_screen)
        self.run_time = time
        self.cap = cv2.VideoCapture(self.camera_source)
        self.run_camera_screen()
        self.cap.release()

    def return_to_start(self):
        self.stop_processes = True

        self.current_screen = 0
        self.app.set_screen(self.current_screen)

    def update_camera_screen(self, status, frame):

        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Fix color
        img_ratio = 2 / 3
        img = PIL.Image.fromarray(img).resize((int(img_ratio * self.app.width), int(img_ratio * self.app.height)), PIL.Image.ANTIALIAS)
        display_image = PIL.ImageTk.PhotoImage(master=self.app.countdown_screen, image=img)
        self.app.camera_image.config(image=display_image)

        self.app.countdown_timer.config(text=status)

        self.app.countdown_timer.update()
        self.app.camera_image.update()

    def update_running_screen(self, status="", title=""):

        if title != "":
            self.app.running_label.config(text=title)
            self.app.running_label.update()

        if status != "":
            self.app.running_timer.config(text = status)
            self.app.running_timer.update()

    def advance_screen(self, new_screen=-1):

        if new_screen != -1:
            self.current_screen = new_screen

        else:
            self.current_screen += 1
            self.current_screen = self.current_screen % 4

        self.app.set_screen(self.current_screen)

        if self.current_screen == 2:
            self.cap = cv2.VideoCapture(self.camera_source)
            self.run_running_screen()
            self.cap.release()
        elif self.current_screen == 1:
            self.cap = cv2.VideoCapture(self.camera_source)
            self.run_camera_screen()
            self.cap.release()

    def run_running_screen(self):

        self.stop_processes = False

        start_time = time.time()

        while True:
            if self.stop_processes:
                return

            ret_val, frame = self.cap.read()
            self.data.append(frame)

            elapsed_time = time.time() - start_time
            if elapsed_time >= self.run_time:
                # self.advance_screen()
                break
            else:
                self.update_running_screen(str(np.round((self.run_time - elapsed_time) * 10) / 10) + " seconds remaining")

        self.update_running_screen("0.0%", "Processing...")
        self.cap.release()

        progress = [0]
        event = threading.Event()
        process_thread = ProcessThread(event, progress, self).start()
        while True:
            if self.stop_processes:
                event.set()
                return

            delta = 0.0001
            if -delta < abs(progress[0] - 1) < delta:
                self.advance_screen()
                break

            self.update_running_screen('{:3.1f}%'.format(100 * progress[0]))
            time.sleep(0.1)

        event.set()

        self.update_running_screen(str(self.run_time) + " seconds remaining", "Running...")

    def run_camera_screen(self):
        # time.sleep(1)
        start_time = time.time()

        while True:
            elapsed_time = time.time() - start_time
            if elapsed_time >= 5.0:
                self.advance_screen()
                break

            ret_val, frame = self.cap.read()

            if frame is None:
                break

            self.update_camera_screen(str(np.round((5.0 - elapsed_time) * 10) / 10), frame)


root = Tk()

root.overrideredirect(True)
root.overrideredirect(False)
root.attributes("-fullscreen", True)

app = GUIManager(root, video)

root.mainloop()
root.destroy()
