import cv2
import numpy as np
import PIL.Image, PIL.ImageTk
import subprocess
import time
import threading

from pydub import AudioSegment
from pydub.playback import play

from argparse import ArgumentParser
from Cameras.gui import App


# Import OpenPose and necessary libraries for OpenPose
import os
import sys
from sys import platform

dir_path = os.path.dirname(os.path.realpath(__file__))
try:
    # OpenPose import
    if platform == 'win32':
        # Change variables to point to the python release folder
        sys.path.append(dir_path + '/../../openpose/windows/python/openpose/Release')
        os.environ['PATH'] = os.environ['PATH'] + ';' + dir_path + '/../../openpose/windows/x64/Release;' + dir_path + '/../../openpose/windows/bin;'
        import pyopenpose as op
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
if not os.path.exists('output/json') and platform != 'win32':
    os.makedirs('output/json')

class ProcessThread(threading.Thread):
    def __init__(self, event, progress, gui):
        threading.Thread.__init__(self)
        self.stopped = event
        self.progress = progress
        self.data = (gui.open_data, gui.closed_data)
        self.length = len(self.data[0]) + len(self.data[1])

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        if platform == 'win32':
            self.writer_open = cv2.VideoWriter('output/processed_output_open_eyes.mp4', fourcc, 30, (gui.vid_width, gui.vid_height))
            self.writer_closed = cv2.VideoWriter('output/processed_output_closed_eyes.mp4', fourcc, 30, (gui.vid_width, gui.vid_height))

            # OpenPose setup
            params = dict()
            params['model_folder'] = 'openpose/models/'
            params['face'] = True
            params['hand'] = True
            self.opWrapper = op.WrapperPython()
            self.opWrapper.configure(params)
            self.opWrapper.start()
            self.datum = op.Datum()
        else:
            self.writer_open = cv2.VideoWriter('output/output_open_eyes.mp4', fourcc, 30, (gui.vid_width, gui.vid_height))
            self.writer_closed = cv2.VideoWriter('output/output_closed_eyes.mp4', fourcc, 30, (gui.vid_width, gui.vid_height))

    def end_process(self, text='Process ended...'):
        self.progress[0] = 1
        print(text)
        self.writer_open.release()
        self.writer_closed.release()

    def run(self):
        frames_completed = 0
        finished_open = False
        length_open = len(self.data[0])
        if self.length <= 0:
            self.stopped.set()
            self.end_process('Processing failed...')
            return

        try:
        # Process a frame each loop on Windows
        # Otherwise write each unedited frame to a file
            while not self.stopped.isSet():
                frame = frames_completed
                if finished_open:
                    frame -= length_open
                data = self.data[1 if finished_open else 0][frame]
                if platform == 'win32':
                    self.datum.cvInputData = data
                    self.opWrapper.emplaceAndPop([self.datum])
                    if finished_open:
                        self.writer_closed.write(self.datum.cvOutputData)
                    else:
                        self.writer_open.write(self.datum.cvOutputData)
                else:
                    if finished_open:
                        self.writer_closed.write(data)
                    else:
                        self.writer_open.write(data)

                frames_completed += 1
                if platform == 'win32':
                    self.progress[0] = frames_completed / self.length
                    if frames_completed >= self.length:
                        self.stopped.set()
                        self.end_process('Processing complete...')
                        return
                else:
                    if frames_completed >= self.length:
                        break
                if frames_completed == length_open:
                    finished_open = True
            if platform == 'win32':
                self.end_process('Processing terminated...')
                return

            # Process video on a non-Windows machine
            self.writer_open.release()
            self.writer_closed.release()
            process = subprocess.Popen(['/bin/bash', 'scripts/run_openpose.sh'])
            while process.poll() is None:
                self.progress[0] = len(os.listdir('output/json')) / self.length
                time.sleep(5)
            self.end_process('Processing complete...')
        except Exception as e:
            self.end_process('Processing failed...')
            print(e)


class GUIManager:
    def __init__(self, camera_source=0):
        # Constants
        self.OPEN_EYES = True
        self.CLOSED_EYES = False

        self.current_screen = 0
        self.run_time = 15.0
        self.stop_processes = False

        self.camera_source = camera_source
        self.cap = cv2.VideoCapture(self.camera_source)
        self.vid_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.vid_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)

        self.open_data, self.closed_data = [], []

    def get_alert_sound(self):
        self.ding_sound = AudioSegment.from_wav("./media/Ding.wav")

    def run_gui(self):
        self.app = App(self)
        self.app.start_gui()

    def start(self, countdown_time, time):
        self.current_screen = 1
        self.app.set_screen(self.current_screen)
        self.countdown_time = countdown_time
        self.run_time = time

        self.run_camera_screen()

    def return_to_start(self):
        self.stop_processes = True
        self.open_data, self.closed_data = [], []
        self.current_screen = 0
        self.app.set_screen(self.current_screen)

    def update_result_screen(self, frame):
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Fix color
        img_ratio = 2 / 3
        img = PIL.Image.fromarray(img).resize((int(img_ratio * self.app.width), int(img_ratio * self.app.height)),
                                              PIL.Image.ANTIALIAS)
        display_image = PIL.ImageTk.PhotoImage(master=self.app.results_screen, image=img)
        self.app.result_image.config(image=display_image)

        self.app.result_image.update()

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

        if self.current_screen == 3:
            self.run_results_screen()
        elif self.current_screen == 2:
            self.run_running_screen()
        elif self.current_screen == 1:
            self.run_camera_screen()

    def do_processing(self):
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

    def do_running(self, eye_status):
        # eye_status is whether or not the eyes are open
        total_frames = int(self.fps * self.run_time)
        current_frame = 0

        while True:
            if self.stop_processes:
                return

            ret_val, frame = self.cap.read()
            if eye_status == self.CLOSED_EYES:
                self.closed_data.append(frame)
            elif eye_status == self.OPEN_EYES:
                self.open_data.append(frame)
            else:
                return
            current_frame += 1

            if current_frame >= total_frames:
                # self.advance_screen()
                break
            else:
                self.update_running_screen(str(np.round((self.run_time - (current_frame / self.fps)) * 10) / 10) + " seconds remaining")

    def run_running_screen(self):
        self.stop_processes = False

        self.do_running(self.OPEN_EYES)

        self.update_running_screen(str(self.countdown_time) + " seconds remaining", "Close eyes for second recording")

        start_time = time.time()

        while True:
            if self.stop_processes:
                return

            elapsed_time = time.time() - start_time
            if elapsed_time >= self.countdown_time:
                # self.advance_screen()
                break
            else:
                self.update_running_screen(str(np.round((self.countdown_time - elapsed_time) * 10) / 10) + " seconds remaining")

        self.update_running_screen(str(self.countdown_time) + " seconds remaining", "Running...")

        self.do_running(self.CLOSED_EYES)

        play(self.ding_sound)

        self.update_running_screen("0.0%", "Processing...")
        self.do_processing()
        self.update_running_screen(str(self.run_time) + " seconds remaining", "Running...")

    def run_camera_screen(self):
        start_time = time.time()
        elapsed_time = 0
        while True:
            elapsed_time = time.time() - start_time
            if elapsed_time >= self.countdown_time:
                self.advance_screen()
                break

            ret_val, frame = self.cap.read()

            if frame is None:
                break

            self.update_camera_screen(str(np.round((self.countdown_time - elapsed_time) * 10) / 10), frame)

    def get_video_frames(self, video):
        frames = []
        cap = cv2.VideoCapture(video)
        ret_val, frame = cap.read()
        while frame is not None:
            frames.append(frame)
            ret_val, frame = cap.read()
        cap.release()
        return frames

    def run_results_screen(self):
        frames = self.get_video_frames('output/processed_output_open_eyes.mp4')
        frames += self.get_video_frames('output/processed_output_closed_eyes.mp4')
        start_time = time.time()
        while not self.stop_processes:
            for frame in frames:
                self.update_result_screen(frame)
                if (time.time() - start_time >= 60):
                    self.return_to_start()
                time.sleep(0.5/self.fps)
