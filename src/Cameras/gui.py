import threading

import PIL.Image, PIL.ImageTk
import cv2
import time
import numpy as np

from argparse import ArgumentParser
from tkinter import *

parser = ArgumentParser()
parser.add_argument('--video', default='0', dest='video', type=str, help='The path to a video or number of the camera used for capture.')
video = parser.parse_args().video
try:
    video = int(video)
except ValueError:
    pass

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


class App:

    def __init__(self, master, camera_source=0):

        self.stop_processes = False

        self.cap = cv2.VideoCapture(camera_source)
        vid_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        vid_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.writer = cv2.VideoWriter('output.mp4', fourcc, 30, (vid_width, vid_height))

        self.current_screen = 0

        relief_pattern = RIDGE
        border_width = 10

        #Main Screen
        self.main_screen = Frame(master, borderwidth=border_width, relief=relief_pattern)
        self.main_screen.place(relwidth=1.0, relheight=1.0)

        self.width = self.main_screen.winfo_screenwidth()
        self.height = self.main_screen.winfo_screenheight()

        self.main_title = Label(self.main_screen, text="Instructions", font=("Times New Roman", 48), pady=50)
        self.main_title.pack()

        instructions = "This system will measure how much you sway when trying to stand still. To begin, press start. A screen will appear showing you the camera's perspective; stand in the center of the camera's view, facing the camera. After a count-down, the camera will start recording. Stand still during this time. Once done recording, the recording will be processed and you'll be able to see the results."
        self.main_instructions = Label(self.main_screen, text=instructions, font=("Times New Roman", 24), pady=50, wraplength=self.width - 200.0, justify=CENTER)
        self.main_instructions.pack()

        self.length_title = Label(self.main_screen, text="Length of Test", font=("Times New Roman", 24), pady=50, wraplength=self.width - 200.0, justify=CENTER)
        self.length_title.pack()

        self.length_box = Entry(self.main_screen, font=("Times New Roman", 24), justify=CENTER)
        self.length_box.insert(INSERT, "5.0")
        self.length_box.pack()

        self.start_button = Button(self.main_screen, text="Start", font=("Times New Roman", 24), width=15, pady=10, command=self.advance_screen)
        self.start_button.pack()

        #Countdown Screen
        self.countdown_screen = Frame(master, borderwidth=border_width, relief=relief_pattern)

        self.camera_image = Label(self.countdown_screen)
        self.camera_image.pack()

        Label(self.countdown_screen, text="Countdown", font=("Times New Roman", 48), justify=CENTER).pack()

        self.countdown_timer = Label(self.countdown_screen, text="5.0", font=("Times New Roman", 48), justify=CENTER)
        self.countdown_timer.pack()

        Label(self.countdown_screen, text="seconds until start", font=("Times New Roman", 48), justify=CENTER).pack()


        # self.next_button = Button(self.countdown_screen, text="Next", font=("Times New Roman", 24), width=15, pady=10, command=self.advance_screen)
        # self.next_button.pack()



        #Running Screen
        self.running_screen = Frame(master, borderwidth=border_width, relief=relief_pattern)
        # self.running_screen = Button(self.running_screen, text="Continue", font=("Times New Roman", 24), width=15, pady=10, command=self.advance_screen)
        # self.running_screen.pack()

        self.running_label = Label(self.running_screen, text="Running...", font=("Times New Roman", 48), pady=100, justify=CENTER)
        self.running_label.pack()

        self.running_timer = Label(self.running_screen, text="5.0", font=("Times New Roman", 48), pady=10, justify=CENTER)
        self.running_timer.pack()

        self.quit_button = Button(self.running_screen, text="Back", font=("Times New Roman", 24), pady=10, command=self.return_to_start)
        self.quit_button.pack()



        #Results Screen
        self.results_screen = Frame(master, borderwidth=border_width, relief=relief_pattern)

        Label(self.results_screen, text="Results", font=("Times New Roman", 64), justify=CENTER, pady=50.0).pack()

        results = "Sway averaged 0.2 m/s/s across the test."
        self.main_instructions = Label(self.results_screen, text=results, font=("Times New Roman", 36), pady=50, wraplength=self.width - 200.0, justify=CENTER)
        self.main_instructions.pack()

        self.back_button = Button(self.results_screen, text="Back", font=("Times New Roman", 24), width=15, pady=10, command=self.advance_screen)
        self.back_button.pack()



        # self.show = Button(self.countdown_screen, text="Show", command=self.show_frame)
        # self.show.pack()
        #
        # self.button = Button(
        #     self.main_screen, text="QUIT", fg="red", command=master.quit
        # )
        # self.button.pack()
        #
        # self.hide = Button(self.main_screen, text="Hide", command=self.hide_frame)
        # self.hide.pack()

        self.master = master

    def run_camera_screen(self):

        start_time = time.time()

        while True:
            elapsed_time = time.time() - start_time
            if elapsed_time >= 5.0:
                self.advance_screen()
                break
            else:
                self.countdown_timer.config(text=str(np.round((5.0 - elapsed_time) * 10)/10))
                self.countdown_timer.update()

            ret_val, frame = self.cap.read()

            if frame is None:
                break

            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Fix color
            img_ratio = 2 / 3
            img = PIL.Image.fromarray(img).resize((int(img_ratio * self.width), int(img_ratio * self.height)),
                                                  PIL.Image.ANTIALIAS)
            display_image = PIL.ImageTk.PhotoImage(master=self.countdown_screen, image=img)

            self.camera_image.config(image = display_image)
            self.camera_image.update()

    def run_running_screen(self):

        self.stop_processes = False

        start_time = time.time()

        while True:

            if self.stop_processes:
                return

            elapsed_time = time.time() - start_time
            if elapsed_time >= 5.0:
                # self.advance_screen()
                break
            else:
                self.running_timer.config(text=(str(np.round((5.0 - elapsed_time) * 10)/10) + " seconds remaining"))
                self.running_timer.update()

        self.running_label.config(text="Processing...")

        progress = [0]
        event = threading.Event()
        process_thread = ProcessThread(event, 15, 0.1, progress).start()
        while True:

            if self.stop_processes:
                event.set()
                return

            # print('Main thread: ' + str(progress[0]))
            delta = 0.0001
            if -delta < abs(progress[0] - 1) < delta:
                self.advance_screen()
                break
            # num.setText('{:3.1f}%'.format(100 * progress[0]))
            self.running_timer.config(text='{:3.1f}%'.format(100 * progress[0]))
            self.running_timer.update()
            time.sleep(0.1)

        self.running_label.config(text="Running...")
        self.running_timer.config(text="5.0 seconds remaining")

    def return_to_start(self):
        self.stop_processes = True
        self.running_label.config(text="Running...")
        self.running_timer.config(text="5.0 seconds remaining")
        self.advance_screen(0)

    def advance_screen(self, new_screen=-1):

        screens = [self.main_screen, self.countdown_screen, self.running_screen, self.results_screen]

        if new_screen != -1:

            screens[self.current_screen].place_forget()
            screens[new_screen].place(relwidth=1.0, relheight=1.0)
            self.current_screen = new_screen

        else:
            self.current_screen += 1
            self.current_screen = self.current_screen % 4

            if self.current_screen == 0:
                screens[3].place_forget()
                screens[0].place(relwidth=1.0, relheight=1.0)
            else:
                screens[self.current_screen - 1].place_forget()
                screens[self.current_screen].place(relwidth=1.0, relheight=1.0)

        if self.current_screen == 1:
            self.run_camera_screen()
        elif self.current_screen == 2:
            self.run_running_screen()


root = Tk()

root.overrideredirect(True)
root.overrideredirect(False)
root.attributes("-fullscreen", True)

app = App(root)

root.mainloop()
root.destroy()
