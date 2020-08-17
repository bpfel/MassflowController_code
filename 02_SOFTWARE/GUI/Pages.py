from setup import Setup
from GUI.Views import DiagnosticView
import tkinter as tk
import logging
from matplotlib import style

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
        label = tk.Label(
            self.static_header, textvariable="WIP title", font=LARGE_FONT, background="white"
        )
        label.grid(column=2, columnspan=2, row=0, sticky="nwes")

        self.views = {
            DiagnosticView: DiagnosticView(master=self.dynamic_main, figures=self.figures, setup=self.setup)
        }
        killbuton = tk.Button(master=self.static_header, text="Let the world burn", command=self.views[DiagnosticView].destroy_widgets)
        killbuton.grid(column=1, row=0, sticky="nwes")
        restorebuton = tk.Button(master=self.static_header,
                                 text="Resurrect", command=self.views[DiagnosticView].load_widgets)
        restorebuton.grid(column=0, row=0, sticky="nwes")

        # configure weighting of rows and columns upon resizing
        self.dynamic_main.columnconfigure(0, weight=1)
        self.dynamic_main.columnconfigure(1, weight=100)
        self.dynamic_main.rowconfigure(0, weight=1)
        self.dynamic_main.rowconfigure(1, weight=1)

        self.views[DiagnosticView].load_widgets()
