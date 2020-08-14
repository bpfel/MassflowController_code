from setup import Setup
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import tkinter as tk
from tkinter import messagebox
from copy import deepcopy
import logging
from GUI.LivePlotHandler import LivePlotHandler
from GUI.WidgetFactory import WidgetFactory
from abc import abstractmethod

logger = logging.getLogger("root")

matplotlib.use("TkAgg")
UPDATE_TIME = 100


class WidgetComposer:
    def __init__(self, setup: Setup):
        self.setup = setup
        self.figures = {}
        self.axes = {}
        self.animations = {}
        self.app = None
        self.widget_factory = None
        # Set up the app
        self.set_up_app()

        # Establish main frame
        self.main_frame = tk.Frame(self.app)
        self.main_frame.grid(row=0, column=0, sticky="nsew")

        # set up steps
        self.set_up_live_plots()
        self.set_up_widget_factory()


        # Load the initial view
        self.diagnostic_view = DiagnosticView(master=self.main_frame, widget_factory=self.widget_factory)
        self.diagnostic_view.activate_widgets()
        self.main_frame.tkraise()
        self.run()

    def set_up_live_plots(self):
        # Create figures
        self.figures = {
            "diagnostic_temperatures": None,
            "diagnostic_flows": None,
            "diagnostic_delta_temperatures": None,
            "diagnostic_PWM": None,
            "graph": None,
            "pid_components": None,
        }
        self.axes = deepcopy(self.figures)
        for figure_name in self.figures.keys():
            fig, ax = plt.subplots()
            self.figures[figure_name] = fig
            self.axes[figure_name] = ax

        # Create Live Plots
        pid = LivePlotHandler(
            ax=self.axes["pid_components"],
            fig=self.figures["pid_components"],
            title="PID Components",
            ylabel="Gain []",
            ylims=(-2, 2),
            signal_buffers=[
                self.setup.measurement_buffer["Controller Output P"],
                self.setup.measurement_buffer["Controller Output I"],
                self.setup.measurement_buffer["Controller Output D"],
            ],
            time_buffer=self.setup.measurement_buffer["Time"],
            line_styles=["b-", "r-", "g-"],
            legend_entries=["P", "I", "D"],
            interval=self.setup.interval_s,
        )
        self.animations["pid_components"] = animation.FuncAnimation(
            fig=self.figures["pid_components"],
            func=pid,
            blit=True,
            interval=UPDATE_TIME,
        )

        temp = LivePlotHandler(
            ax=self.axes["diagnostic_temperatures"],
            fig=self.figures["diagnostic_temperatures"],
            title="Temperatures",
            ylabel="Temperature [deg C]",
            ylims=(20, 40),
            signal_buffers=[
                self.setup.measurement_buffer["Temperature 1"],
                self.setup.measurement_buffer["Temperature 2"],
            ],
            time_buffer=self.setup.measurement_buffer["Time"],
            line_styles=["b-", "k-"],
            legend_entries=["T1", "T2"],
            interval=self.setup.interval_s,
        )
        self.animations["diagnostic_temperatures"] = animation.FuncAnimation(
            fig=self.figures["diagnostic_temperatures"],
            func=temp,
            blit=True,
            interval=UPDATE_TIME,
        )

        flow = LivePlotHandler(
            ax=self.axes["diagnostic_flows"],
            fig=self.figures["diagnostic_flows"],
            title="Flow",
            ylabel="Flow [slm]",
            ylims=(0, 100),
            signal_buffers=[
                self.setup.measurement_buffer["Flow"],
                self.setup.measurement_buffer["Flow Estimate"],
            ],
            time_buffer=self.setup.measurement_buffer["Time"],
            line_styles=["b-", "k-"],
            legend_entries=["SFM", "Estimate"],
            interval=self.setup.interval_s,
        )
        self.animations["diagnostic_flows"] = animation.FuncAnimation(
            fig=self.figures["diagnostic_flows"],
            func=flow,
            blit=True,
            interval=UPDATE_TIME,
        )

        delta_t = LivePlotHandler(
            ax=self.axes["diagnostic_delta_temperatures"],
            fig=self.figures["diagnostic_delta_temperatures"],
            title="Temperature Difference",
            ylabel="dT [deg C]",
            ylims=(0, 20),
            signal_buffers=[
                self.setup.measurement_buffer["Temperature Difference"],
                self.setup.measurement_buffer["Target Delta T"],
            ],
            time_buffer=self.setup.measurement_buffer["Time"],
            line_styles=["k-", "r-"],
            legend_entries=["\Delta T", "Target \Delta T"],
            interval=self.setup.interval_s,
        )

        self.animations["diagnostic_delta_temperatures"] = animation.FuncAnimation(
            fig=self.figures["diagnostic_delta_temperatures"],
            func=delta_t,
            blit=True,
            interval=UPDATE_TIME,
        )

        pwm = LivePlotHandler(
            ax=self.axes["diagnostic_PWM"],
            fig=self.figures["diagnostic_PWM"],
            title="Power",
            ylabel="PWM",
            ylims=(0, 1),
            signal_buffers=[self.setup.measurement_buffer["PWM"]],
            time_buffer=self.setup.measurement_buffer["Time"],
            line_styles=["-k"],
            legend_entries=["PWM Output"],
            interval=self.setup.interval_s,
        )
        self.animations["diagnostic_PWM"] = animation.FuncAnimation(
            fig=self.figures["diagnostic_PWM"],
            func=pwm,
            blit=True,
            interval=UPDATE_TIME,
        )

    def set_up_app(self):
        self.app = tk.Tk()
        self.app.wm_title("Mass Flow Measurement")
        self.app.iconbitmap("GUI/icon.ico")

    def set_up_widget_factory(self):
        self.widget_factory = WidgetFactory(
            setup=self.setup,
            initial_parent=self.main_frame,
            figures=self.figures)

    def run(self):
        self.app.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.app.mainloop()

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.app.quit()


BACKGROUND = "#ffffff"


class BasicView(tk.Frame):
    def __init__(self, master, widget_factory):
        super(BasicView, self).__init__(master=master, background=BACKGROUND)
        self.widget_factory = widget_factory

        # Set up basic frames
        self.HEADER = tk.Frame(master=self, background=BACKGROUND)
        self.MAIN = tk.Frame(master=self, background=BACKGROUND)
        self.FOOTER = tk.Frame(master=self, background=BACKGROUND)

        # Arrange basic frames
        self.HEADER.grid(row=0, sticky="nwes")
        self.MAIN.grid(row=1, sticky="nwes")
        self.FOOTER.grid(row=2, sticky="nwes")

        # Configure row weights to allow automatic adjustment to scaling
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)

        lable = tk.Label(self.HEADER, text="Start Page")
        lable.grid(column=0, pady=10, padx=10)


class DiagnosticView(BasicView):
    def __init__(self, master, widget_factory):
        super(DiagnosticView, self).__init__(master=master, widget_factory=widget_factory)
        self.CONTROLS = None
        self.PLOTS = None

        self.set_up_geometry()

    def set_up_geometry(self):
        # Set up second level frames
        self.CONTROLS = tk.Frame(master=self.MAIN, background=BACKGROUND)
        self.PLOTS = tk.Frame(master=self.MAIN, background=BACKGROUND)

        # Arrange second level frames
        self.CONTROLS.grid(column=0, sticky="nwes")
        self.PLOTS.grid(column=1, sticky="nwes")

        # Configure column weights to allow automatic adjustment to scaling
        self.MAIN.columnconfigure(0, weight=100)
        self.MAIN.columnconfigure(1, weight=1)

        # Attach this frame to its parent
        self.grid(row=0, column=0)

    def activate_widgets(self):
        pass
        # self.widget_factory.test_widgets["test"].widget.grid(in_=self.CONTROLS, row=0, column=0)
        # self.widget_factory.test_widgets["test"].grid_forget()
        # self.widget_factory.test_widgets["test"].grid(in_=self.CONTROLS, row=0, column=0)
