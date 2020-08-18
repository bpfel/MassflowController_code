from setup import Setup
from GUI.Views import DiagnosticView, PWMSettingTrainingView
import tkinter as tk
import logging
from matplotlib import style
from functools import partial
from PIL import ImageTk, Image

logger = logging.getLogger("root")

LARGE_FONT = ("Verdana", 12)
MEDIUM_GRAY = "#d0d0d0"
WHITE = "#ffffff"
style.use("ggplot")


class TkGUI(tk.Frame):
    def __init__(self, figures, setup: Setup, controller):
        super(TkGUI, self).__init__()
        self.pack(side="top", fill="both", expand=True)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.figures = figures
        self.controller = controller

        self.frames = {
            EmptyPage: EmptyPage(parent=self, controller=self),
            ExperimentPage: ExperimentPage(
                parent=self,
                controller=self.controller,
                figures=self.figures,
                setup=setup,
            ),
        }

        for F in self.frames.values():
            F.grid(row=0, column=0, sticky="nsew")


class EmptyPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, background="white")


class ExperimentPage(tk.Frame):
    def __init__(self, parent, controller, figures, setup: Setup):
        self.controller = controller
        self.setup = setup
        self.figures = figures
        self.parent = parent

        ###########
        # Level 0 #
        ###########
        tk.Frame.__init__(self, master=parent, background="white")
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=20)
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)

        ###########
        # Level 1 #
        ###########
        self.static_header = tk.Frame(master=self, background="white")
        self.dynamic_main = tk.Frame(master=self, background="white")
        self.static_footer = tk.Frame(master=self, background="white", height=50)

        self.views = [
            DiagnosticView(
                master=self.dynamic_main, figures=self.figures, setup=self.setup
            ),
            PWMSettingTrainingView(
                master=self.dynamic_main, figures=self.figures, setup=self.setup
            ),
        ]

        self.current_view = 0
        self.title_variable = tk.StringVar(master=self, value=self.views[0].title)

        self.static_header.grid(row=0, column=0, sticky="nwes")
        self.static_header.columnconfigure(0, weight=2)
        self.static_header.columnconfigure(1, weight=1)
        self.static_header.columnconfigure(2, weight=2)
        self.static_header.rowconfigure(0, weight=1)
        self.header_left = tk.Frame(master=self.static_header, background="white")
        self.header_center = tk.Frame(master=self.static_header, background="white")
        self.header_right = tk.Frame(master=self.static_header, background="white")
        self.header_left.grid(row=0, column=0)
        self.header_center.grid(row=0, column=1)
        self.header_right.grid(row=0, column=2)

        self.dynamic_main.grid(row=1, column=0, sticky="nwes")

        self.static_footer.grid(row=2, column=0, sticky="nsew")
        self.static_footer.columnconfigure(0, weight=20)
        self.static_footer.columnconfigure(1, weight=1)
        self.static_footer.columnconfigure(2, weight=20)
        self.footer_left = tk.Frame(master=self.static_footer, background="white")
        self.footer_center = tk.Frame(master=self.static_footer, background="white")
        self.footer_right = tk.Frame(master=self.static_footer, background="white")
        self.footer_left.grid(row=0, column=0, sticky="nwes")
        self.footer_center.grid(row=0, column=1, sticky="nwes")
        self.footer_right.grid(row=0, column=2, sticky="nwes")

        self.logo_eth = self.place_logo(
            master=self.footer_left,
            img_file_location="GUI/eth.png",
            height=40,
            side="left",
        )
        self.logo_sensirion = self.place_logo(
            master=self.footer_right,
            img_file_location="GUI/sensirion.png",
            height=40,
            side="right",
        )

        label = tk.Label(
            self.header_center,
            textvariable=self.title_variable,
            font=("Arial Black", 14),
            background="white",
        )
        label.pack(fill="x")

        # Create a stop button to pause the measurement

        def start_stop_measurement(setup=setup):
            if stop_measurement_button["text"] == "Stop":
                stop_measurement_button["text"] = "Start"
                setup.stop_measurement_thread()
            elif stop_measurement_button["text"] == "Start":
                stop_measurement_button["text"] = "Stop"
                setup.start_measurement_thread()
            else:
                raise RuntimeError("Invalid button state!")

        stop_measurement_button = tk.Button(
            master=self.footer_center,
            text="Stop",
            command=partial(start_stop_measurement, setup=self.setup),
            bg="red",
            fg="white",
            font=("Arial Black", "14"),
        )
        stop_measurement_button.pack(padx=20, pady=20, fill="x")

        next_view_button = tk.Button(
            master=self.header_right,
            text="Next",
            command=partial(self.next_view),
            bg="blue",
            fg="white",
            font=("Arial Black", "14"),
        )
        next_view_button.pack(side="top")

        previous_view_button = tk.Button(
            master=self.header_left,
            text="Previous",
            command=partial(self.previous_view),
            bg="blue",
            fg="white",
            font=("Arial Black", "14"),
        )
        previous_view_button.pack(side="top")

        self.views[self.current_view].load_widgets()

    def place_logo(self, master, img_file_location, height, side):
        img = Image.open(img_file_location)
        (size_x, size_y) = img.size
        factor = size_y / height
        size_x = int(size_x / factor)
        img = ImageTk.PhotoImage(img.resize((size_x, height)))
        label = tk.Label(master=master, image=img, background="white")
        label.pack(fill=None, expand=False, side=side)
        return img

    def next_view(self):
        if not self.current_view < len(self.views) - 1:
            return
        else:
            self.parent.frames[EmptyPage].tkraise()
            self.views[self.current_view].destroy_widgets()
            self.current_view += 1
            self.views[self.current_view].load_widgets()
            self.parent.frames[ExperimentPage].tkraise()

    def previous_view(self):
        if self.current_view == 0:
            return
        else:
            self.parent.frames[EmptyPage].tkraise()
            self.views[self.current_view].destroy_widgets()
            self.current_view -= 1
            self.views[self.current_view].load_widgets()
            self.parent.frames[ExperimentPage].tkraise()
