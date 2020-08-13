from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from setup import Setup
import tkinter as tk
from tkinter import DISABLED, NORMAL, HORIZONTAL
from tkinter import ttk
from matplotlib import style
from tkinter import messagebox
from functools import partial
import logging
from GUI.Pages.Diagnostic import DiagnosticView

logger = logging.getLogger("root")

LARGE_FONT = ("Verdana", 12)
MEDIUM_GRAY = "#d0d0d0"
WHITE = "#ffffff"
style.use("ggplot")


class TkGUI(tk.Tk):
    def __init__(self, figures, setup: Setup, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.figures = figures

        self.wm_title("Mass Flow Measurement")
        self.iconbitmap("GUI/icon.ico")

        # container = tk.Frame(self)
        container = ttk.Notebook(self, style="TNotebook")
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {
            StartPage: StartPage(parent=container, controller=self),
            DiagnosticView: DiagnosticView(
                parent=container, controller=self, figures=self.figures, setup=setup
            ),
            PWMSettingTraining: PWMSettingTraining(
                parent=container, controller=self, figure=self.figures["pid_components"],
                setup=setup
            ),
        }

        for F in self.frames.values():
            F.grid(row=0, column=0, sticky="nsew")
            container.add(F, text=str(F))

        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    def run(self):
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.mainloop()

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.quit()


class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Start Page", font=LARGE_FONT)
        label.pack(pady=10, padx=10)




class PageTwo(tk.Frame):
    def __init__(self, parent, controller, figure):
        self.figure = figure
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Page Two!!!", font=LARGE_FONT)
        label.pack(pady=10, padx=10)


class PWMSettingTraining(tk.Frame):
    def __init__(self, parent, controller, figure, setup):
        self.figure = figure
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Graph Page!", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        canvas = FigureCanvasTkAgg(self.figure, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        toolbar.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.power_scale = tk.Scale(
            master=self,
            from_=0,
            to=1,
            label="Power",
            background="white",
            resolution=0.01,
            showvalue=True,
            orient=HORIZONTAL,
            tickinterval=1 / 5.0,
            command=setup.wrap_set_pwm,
            length=400,
        )
        self.power_scale.set(0)
        self.power_scale.pack(side="top", padx=10, pady=10)

        def start_stop_measurement(setup=setup):
            if stop_measurement_button["text"] == "Stop":
                stop_measurement_button["text"] = "Start"
                setup.stop_measurement_thread()
            elif stop_measurement_button["text"] == "Start":
                stop_measurement_button["text"] = "Stop"
                setup.start_measurement_thread()
            else:
                raise RuntimeError('Invalid button state!')

        stop_measurement_button = tk.Button(
            master=self,
            text='Stop',
            command=partial(start_stop_measurement, setup=setup)
        )
        stop_measurement_button.pack(side="top", padx=10, pady=10)
