import threading

import PIL.Image, PIL.ImageTk
import cv2
import time
import numpy as np

from argparse import ArgumentParser
from gui import App

from tkinter import *


parser = ArgumentParser()
parser.add_argument('--video', default='0', dest='video', type=str, help='The path to a video or number of the camera used for capture.')
video = parser.parse_args().video
try:
    video = int(video)
except ValueError:
    video = 0


class ProcessThread(threading.Thread):
    def __init__(self, event, length, interval, progress):
        threading.Thread.__init__(self)
        self.stopped = event
        self.length = length
        self.interval = self.length if interval > self.length else interval
        self.progress = progress

    def run(self):
        while not self.stopped.wait(self.interval):
            self.progress[0] += self.interval / self.length
            delta = 0.0001
            if -delta < abs(self.progress[0] - 1) < delta:
                self.stopped.set()
                print('Processing complete...')
                return

class GUIManager:

    def __init__(self, master, camera_source=0):

        self.current_screen = 0
        self.app = App(self, master)
        self.run_time = 15.0

        self.stop_processes = False

        self.cap = cv2.VideoCapture(camera_source)
        vid_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        vid_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.writer = cv2.VideoWriter('output.mp4', fourcc, 30, (vid_width, vid_height))

    def start(self, time):
        self.current_screen = 1
        self.app.set_screen(self.current_screen)
        self.run_time = time

        self.run_camera_screen()

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
            self.run_running_screen()
        elif self.current_screen == 1:
            self.run_camera_screen()

    def run_running_screen(self):

        self.stop_processes = False

        start_time = time.time()

        while True:

            if self.stop_processes:
                return

            elapsed_time = time.time() - start_time
            if elapsed_time >= self.run_time:
                # self.advance_screen()
                break
            else:
                self.update_running_screen(str(np.round((self.run_time - elapsed_time) * 10) / 10) + " seconds remaining")

        self.update_running_screen(title="Processing...")

        progress = [0]
        event = threading.Event()
        process_thread = ProcessThread(event, 15, 0.1, progress).start()
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