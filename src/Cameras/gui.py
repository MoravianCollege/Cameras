from tkinter import *

class App:

    def __init__(self, parent):

        self.master = Tk()

        self.master.overrideredirect(True)
        self.master.overrideredirect(False)
        self.master.attributes("-fullscreen", True)

        self.parent = parent

        self.current_screen = 0

        relief_pattern = RIDGE
        border_width = 10

        #Main Screen
        self.main_screen = Frame(self.master, borderwidth=border_width, relief=relief_pattern)
        self.main_screen.place(relwidth=1.0, relheight=1.0)

        self.width = self.main_screen.winfo_screenwidth()
        self.height = self.main_screen.winfo_screenheight()

        self.main_title = Label(self.main_screen, text="Instructions", font=("Times New Roman", 48), pady=50)
        self.main_title.pack()

        instructions = "This system will measure how much you sway when trying to stand still. To begin, press start. A screen will appear showing you the camera's perspective; stand in the center of the camera's view, facing the camera. After a count-down, the camera will start recording. Stand still during this time. Once done recording, the recording will be processed and you'll be able to see the results."
        self.main_instructions = Label(self.main_screen, text=instructions, font=("Times New Roman", 24), pady=50, wraplength=self.width - 200.0, justify=CENTER)
        self.main_instructions.pack()

        self.length_title = Label(self.main_screen, text="Length of Test (seconds)", font=("Times New Roman", 24), wraplength=self.width - 200.0, justify=CENTER)
        self.length_title.pack()

        self.length_container = Frame(self.main_screen, pady=20)
        self.length_container.pack()

        self.length_setting = StringVar()
        self.length_setting.set("5.0")
        self.length_box = Entry(self.length_container, textvariable=self.length_setting, font=("Times New Roman", 24), justify=CENTER)
        self.length_box.pack()

        self.start_button = Button(self.main_screen, text="Start", font=("Times New Roman", 24), width=15, pady=10, command=self.start_button)
        self.start_button.pack()

        #Countdown Screen
        self.countdown_screen = Frame(self.master, borderwidth=border_width, relief=relief_pattern)

        self.camera_image = Label(self.countdown_screen)
        self.camera_image.pack()

        Label(self.countdown_screen, text="Countdown", font=("Times New Roman", 48), justify=CENTER).pack()

        self.countdown_timer = Label(self.countdown_screen, text="5.0", font=("Times New Roman", 48), justify=CENTER)
        self.countdown_timer.pack()

        Label(self.countdown_screen, text="seconds until start", font=("Times New Roman", 48), justify=CENTER).pack()


        #Running Screen
        self.running_screen = Frame(self.master, borderwidth=border_width, relief=relief_pattern)
        # self.running_screen = Button(self.running_screen, text="Continue", font=("Times New Roman", 24), width=15, pady=10, command=self.advance_screen)
        # self.running_screen.pack()

        self.running_label = Label(self.running_screen, text="Running...", font=("Times New Roman", 48), pady=100, justify=CENTER)
        self.running_label.pack()

        self.running_timer = Label(self.running_screen, text="5.0", font=("Times New Roman", 48), pady=10, justify=CENTER)
        self.running_timer.pack()

        self.quit_button = Button(self.running_screen, text="Back", font=("Times New Roman", 24), pady=10, command=self.parent.return_to_start)
        self.quit_button.pack()


        #Results Screen
        self.results_screen = Frame(self.master, borderwidth=border_width, relief=relief_pattern)

        Label(self.results_screen, text="Results", font=("Times New Roman", 64), justify=CENTER, pady=50.0).pack()

        results = "Sway averaged 0.2 m/s/s across the test."
        self.main_instructions = Label(self.results_screen, text=results, font=("Times New Roman", 36), pady=50, wraplength=self.width - 200.0, justify=CENTER)
        self.main_instructions.pack()

        self.back_button = Button(self.results_screen, text="Back", font=("Times New Roman", 24), width=15, pady=10, command=self.parent.return_to_start)
        self.back_button.pack()

        self.screens = [self.main_screen, self.countdown_screen, self.running_screen, self.results_screen]

    def start_gui(self):
        self.master.mainloop()

    def start_button(self):

        run_time = 15.0

        try:
            run_time = float(self.length_setting.get())
        except:
            pass

        self.parent.start(5.0, run_time)

    def set_screen(self, new_screen):
        self.screens[self.current_screen].place_forget()
        self.screens[new_screen].place(relwidth=1.0, relheight=1.0)
        self.current_screen = new_screen

    def __del__(self):
        self.master.destroy()
