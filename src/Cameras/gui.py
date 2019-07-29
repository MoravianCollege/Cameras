from tkinter import *
import cv2
import PIL.Image, PIL.ImageTk


class App:

    def __init__(self, parent):

        self.master = Tk()

        self.master.overrideredirect(True)
        self.master.overrideredirect(False)
        self.master.attributes("-fullscreen", True)

        self.parent = parent

        self.current_screen = 0

        self.background_color = "#DEDEDE"

        relief_pattern = SUNKEN
        border_width = 10

        self.loading_bar_width = int(self.master.winfo_screenwidth() * 0.33)

        #Main Screen
        self.main_screen = Frame(self.master, borderwidth=border_width, relief=relief_pattern, bg=self.background_color)
        self.main_screen.place(relwidth=1.0, relheight=1.0)

        self.width = self.main_screen.winfo_screenwidth()
        self.height = self.main_screen.winfo_screenheight()

        self.image_holder = Frame(self.main_screen, pady=50, bg=self.background_color)
        self.image_holder.pack()

        self.slide_one = Frame(self.image_holder, bg=self.background_color)
        self.slide_one.grid(row=0, column=0)
        self.slide_two = Frame(self.image_holder, bg=self.background_color)
        self.slide_two.grid(row=0, column=1)
        self.slide_three = Frame(self.image_holder, bg=self.background_color)
        self.slide_three.grid(row=0, column=2)

        self.img_size = int(0.25 * self.width)

        self.img_camera = PIL.Image.open("media/CameraGraphic.png").resize((self.img_size, self.img_size), PIL.Image.ANTIALIAS)
        self.camera_graphic = PIL.ImageTk.PhotoImage(self.img_camera)

        self.img_recording = PIL.Image.open("media/RecordingGraphic.png").resize((self.img_size, self.img_size), PIL.Image.ANTIALIAS)
        self.recording_graphic = PIL.ImageTk.PhotoImage(self.img_recording)

        self.img_processing = PIL.Image.open("media/ProcessingGraphic.png").resize((self.img_size, self.img_size), PIL.Image.ANTIALIAS)
        self.processing_graphic = PIL.ImageTk.PhotoImage(self.img_processing)

        self.image_title_one = Label(self.slide_one, text="Step 1 \n Stand in camera's view",
                                     font=("Times New Roman", 30), bg=self.background_color)
        self.image_title_one.pack()
        self.image_one = Label(self.slide_one, image=self.camera_graphic, bg=self.background_color)
        self.image_one.pack()

        self.image_title_two = Label(self.slide_two, text="Step 2 \n Wait for recording",
                                     font=("Times New Roman", 30), bg=self.background_color)
        self.image_title_two.pack()
        self.image_two = Label(self.slide_two, image=self.recording_graphic, bg=self.background_color)
        self.image_two.pack()

        self.image_title_three = Label(self.slide_three, text="Step 3 \n Processing of video",
                                     font=("Times New Roman", 30), bg=self.background_color)
        self.image_title_three.pack()
        self.image_three = Label(self.slide_three, image=self.processing_graphic, bg=self.background_color)
        self.image_three.pack()

        # self.length_title = Label(self.main_screen, text="Length of Test (seconds)", font=("Times New Roman", 24), wraplength=self.width - 200.0, justify=CENTER)
        # self.length_title.pack()
        #
        # self.length_container = Frame(self.main_screen, pady=20)
        # self.length_container.pack()
        #
        # self.length_setting = StringVar()
        # self.length_setting.set("5")
        # self.length_box = Entry(self.length_container, textvariable=self.length_setting, font=("Times New Roman", 24), justify=CENTER)
        # self.length_box.pack()

        self.start_button = Button(self.main_screen, text="Start", font=("Times New Roman", 24), width=15, pady=10, command=self.start_button, bg=self.background_color)
        self.start_button.pack()



        #Countdown Screen
        self.countdown_screen = Frame(self.master, borderwidth=border_width, relief=relief_pattern, bg=self.background_color)

        self.camera_image = Label(self.countdown_screen, bg=self.background_color)
        self.camera_image.pack()

        Label(self.countdown_screen, text="Countdown", font=("Times New Roman", 48), justify=CENTER, bg=self.background_color).pack()

        self.countdown_timer = Label(self.countdown_screen, text="15", font=("Times New Roman", 48), justify=CENTER, bg=self.background_color)
        self.countdown_timer.pack()

        Label(self.countdown_screen, text="seconds until start", font=("Times New Roman", 48), justify=CENTER, bg=self.background_color).pack()



        #Running Screen
        self.running_screen = Frame(self.master, borderwidth=border_width, relief=relief_pattern, bg=self.background_color)
        # self.running_screen = Button(self.running_screen, text="Continue", font=("Times New Roman", 24), width=15, pady=10, command=self.advance_screen)
        # self.running_screen.pack()
        # self.running_screen.place(relwidth=1.0, relheight=1.0)

        self.running_label = Label(self.running_screen, text="Recording...", font=("Times New Roman", 48), pady=100, justify=CENTER, bg=self.background_color)
        self.running_label.pack()

        self.running_timer = Label(self.running_screen, text="5", font=("Times New Roman", 48), pady=10, justify=CENTER, bg=self.background_color)
        self.running_timer.pack()

        self.quit_button = Button(self.running_screen, text="Back", font=("Times New Roman", 24), pady=10, command=self.parent.return_to_start, bg=self.background_color)
        self.quit_button.pack()



        #Processing Screen
        self.processing_screen = Frame(self.master, borderwidth=border_width, relief=relief_pattern, bg=self.background_color)
        # self.processing_screen.place(relwidth=1.0, relheight=1.0)

        self.processing_label = Label(self.processing_screen, text="Processing...", font=("Times New Roman", 48), pady=100,
                                   justify=CENTER, bg=self.background_color)
        self.processing_label.pack()

        self.text_panels = Frame(self.processing_screen, bg=self.background_color)
        self.text_panels.pack()

        self.left_text = ("Current ways of measuring Parkinson's are subjective; this system could be used to obtain objective measures of disease progression. \n"
                          "A system like this could allow patients to measure postural sway on their own, at home. \n"
                          "A 2012 paper explored using accelerometers to measure sway, and found that measuring postural sway could be used to measure the early progression of Parkinson's.")
        self.left_side_text = Label(self.text_panels, text=self.left_text, font=("Times New Roman", 24), padx=25, justify=LEFT, wraplength=self.width/3, bg=self.background_color)
        self.left_side_text.grid(row=0, column=0)

        self.right_text = ("This program uses OpenPose, software which detects human figures in images and maps where there limbs, torso, and body parts are. \n"
                           "Being able to detect where a person's body parts are, a program could analyze their movement, and thus measure postural sway \n"
                           "")
        self.right_side_text = Label(self.text_panels, text=self.right_text, font=("Times New Roman", 24), padx=25, justify=LEFT, wraplength=self.width/3, bg=self.background_color)
        self.right_side_text.grid(row=0, column=1)

        self.processing_percentage = Label(self.processing_screen, text="0%", font=("Times New Roman", 48), pady=10, justify=CENTER, bg=self.background_color)
        self.processing_percentage.pack()

        self.loading_bar_placeholder = Frame(self.processing_screen)
        self.loading_bar_placeholder.pack()
        self.loading_bar = Frame(self.loading_bar_placeholder, height=40, width=550)
        self.loading_bar.pack()

        self.loading_empty = Frame(self.loading_bar, bg="#F3F3F3", height=40, width=self.loading_bar_width)
        self.loading_empty.grid(row=0, column=0, sticky=W)

        self.loading_full = Frame(self.loading_bar, bg="green", height=40, width=0)
        self.loading_full.grid(column=0, row=0, sticky=W)

        # Spacing, cuz the dang pady on the button just makes it bigger... I guess I could set the size of the button to something exact but meh
        Frame(self.processing_screen, height=25, bg=self.background_color).pack()

        self.quit_button = Button(self.processing_screen, text="Back", font=("Times New Roman", 24), pady=10, command=self.parent.return_to_start, bg=self.background_color)
        self.quit_button.pack()



        #Results Screen
        self.results_screen = Frame(self.master, borderwidth=border_width, relief=relief_pattern, bg=self.background_color)

        Label(self.results_screen, text="Results", font=("Times New Roman", 64), justify=CENTER, pady=50.0, bg=self.background_color).pack()

        self.result_image_frame = Frame(self.results_screen, bg=self.background_color)
        self.result_image1 = Label(self.result_image_frame, bg=self.background_color)
        self.result_image2 = Label(self.result_image_frame, bg=self.background_color)

        self.result_image1.grid(row = 0, column = 0)
        self.result_image2.grid(row = 0, column = 1)
        self.result_image_frame.pack()

        results = "Above is a visualization of what OpenPose detects on the video taken of you. Potentially, this information could be used to calculate someone's postural sway, and thus infer how progressed their Parkinson's disease is, or even give a general measure of balance. Further, this could be run on anyone's computer; simply ask a patient to download the program, and they can obtain objective measurements on themselves."
        self.end_results = Label(self.results_screen, text=results, font=("Times New Roman", 36), pady=50, wraplength=self.width - 200.0, justify=CENTER, bg=self.background_color)
        self.end_results.pack()

        self.back_button = Button(self.results_screen, text="Back", font=("Times New Roman", 24), width=15, pady=10, command=self.parent.return_to_start, bg=self.background_color)
        self.back_button.pack()

        self.screens = [self.main_screen, self.countdown_screen, self.running_screen, self.processing_screen, self.results_screen]

    def start_gui(self):
        self.master.mainloop()

    def start_button(self):

        run_time = 0.1

        # try:
        #     run_time = float(self.length_setting.get())
        # except:
        #     pass

        self.parent.start(15.0, run_time)

    def set_screen(self, new_screen):
        self.screens[self.current_screen].place_forget()
        self.screens[new_screen].place(relwidth=1.0, relheight=1.0)
        self.current_screen = new_screen

    def __del__(self):
        self.master.destroy()
