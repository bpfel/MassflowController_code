from setup import Setup
from GUI.Views import DiagnosticView
import tkinter as tk
import logging
from matplotlib import style
from functools import partial

logger = logging.getLogger("root")

LARGE_FONT = ("Verdana", 12)
MEDIUM_GRAY = "#d0d0d0"
WHITE = "#ffffff"
style.use("bmh")


class TkGUI(tk.Frame):
    def __init__(self, figures, setup: Setup, controller):
        super(TkGUI, self).__init__()
        self.pack(side="top", fill="both", expand=True)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.figures = figures
        self.controller = controller

        self.frames = {
            StartPage: StartPage(parent=self, controller=self),
            ExperimentPage: ExperimentPage(
                parent=self,
                controller=self.controller,
                figures=self.figures,
                setup=setup,
            ),
        }

        for F in self.frames.values():
            F.grid(row=0, column=0, sticky="nsew")


class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Start Page", font=LARGE_FONT)
        label.pack(pady=10, padx=10)


class ExperimentPage(tk.Frame):
    def __init__(self, parent, controller, figures, setup: Setup):
        tk.Frame.__init__(self, master=parent, background="white")

        self.setup = setup
        self.figures = figures

        ###########
        # Level 0 #
        ###########
        self.static_header = tk.Frame(master=self, background="white")
        self.dynamic_main = tk.Frame(master=self, background="white")
        self.static_footer = tk.Frame(master=self, background="white")
        self.static_header.grid(row=0, column=0, sticky="nwes")
        self.dynamic_main.grid(row=1, column=0, sticky="nwes")
        self.static_footer.grid(row=1, column=0, sticky="ew")
        self.header_left = tk.Frame(master=self.static_header)
        self.header_center = tk.Frame(master=self.static_header)
        self.header_right = tk.Frame(master=self.static_header)
        self.header_left.grid(row=0, column=0, sticky="nwes")
        self.header_center.grid(row=0, column=1, sticky="nwes")
        self.header_right.grid(row=0, column=2, sticky="nwes")
        self.static_header.columnconfigure(0, weight=1)
        self.static_header.columnconfigure(1, weight=1)
        self.static_header.columnconfigure(2, weight=1)

        label = tk.Label(
            self.header_center,
            textvariable="WIP title",
            font=LARGE_FONT,
            background="white",
        )
        label.pack(fill='x')

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
            master=self.header_left,
            text="Stop",
            command=partial(start_stop_measurement, setup=self.setup),
        )
        stop_measurement_button.pack(side='left')

        self.views = {
            DiagnosticView: DiagnosticView(
                master=self.dynamic_main, figures=self.figures, setup=self.setup
            )
        }

        killbutton = tk.Button(
            master=self.header_left,
            text="Let the world burn",
            command=self.views[DiagnosticView].destroy_widgets,
        )
        killbutton.pack(side='left')
        restorebutton = tk.Button(
            master=self.header_left,
            text="Resurrect",
            command=self.views[DiagnosticView].load_widgets,
        )
        restorebutton.pack(side='left')


        # configure weighting of rows and columns upon resizing
        self.dynamic_main.columnconfigure(0, weight=1)
        self.dynamic_main.columnconfigure(1, weight=100)
        self.dynamic_main.rowconfigure(0, weight=1)
        self.dynamic_main.rowconfigure(1, weight=1)


        self.views[DiagnosticView].load_widgets()
