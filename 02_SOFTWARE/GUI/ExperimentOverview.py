from GUI.Pages import TkGUI
from GUI.LivePlotHandler import LivePlotHandler
from setup import Setup
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from copy import deepcopy
import logging
import tkinter as tk
from tkinter import messagebox
import platform

logger = logging.getLogger("root")

matplotlib.use("TkAgg")
UPDATE_TIME = 100


class ExperimentOverview(tk.Tk):
    def __init__(self, setup: Setup):
        super(ExperimentOverview, self).__init__()
        self.wm_title("Mass Flow Measurement")
        self.iconbitmap("GUI/icon.ico")
        if platform.system() == "Windows":
            self.attributes("-fullscreen", True)
            self.bind(
                "<F11>",
                lambda event: self.attributes(
                    "-fullscreen", not self.attributes("-fullscreen")
                ),
            )
            self.bind("<Escape>", lambda event: self.attributes("-fullscreen", False))
        elif platform.system() == "Linux":
            pass
            # todo: Implement fullscreen for Linux

        self.figures = None
        self.axes = None
        self.setup = setup

        self.set_up_live_plots()
        self.page = TkGUI(figures=self.figures, setup=self.setup, controller=self)
        self.run()

    def run(self):
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.mainloop()

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.quit()

    def set_up_live_plots(self):
        self.figures = {
            "temperatures": None,
            "flows": None,
            "delta_temperatures": None,
            "PWM": None,
            "pid_components": None,
            "dummy": None,
        }
        self.axes = deepcopy(self.figures)
        for figure_name in self.figures.keys():
            fig, ax = plt.subplots(figsize=(4, 4))
            self.figures[figure_name] = fig
            self.axes[figure_name] = ax

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
        self.ani_1 = animation.FuncAnimation(
            fig=self.figures["pid_components"],
            func=pid,
            blit=True,
            interval=UPDATE_TIME,
        )

        temp = LivePlotHandler(
            ax=self.axes["temperatures"],
            fig=self.figures["temperatures"],
            title="Temperatures",
            ylabel="Temperature [deg C]",
            ylims=(00, 60),
            signal_buffers=[
                self.setup.measurement_buffer["Temperature 1"],
                self.setup.measurement_buffer["Temperature 2"],
            ],
            time_buffer=self.setup.measurement_buffer["Time"],
            line_styles=["b-", "k-"],
            legend_entries=["T1", "T2"],
            interval=self.setup.interval_s,
        )
        self.ani_2 = animation.FuncAnimation(
            fig=self.figures["temperatures"],
            func=temp,
            blit=True,
            interval=UPDATE_TIME,
        )

        flow = LivePlotHandler(
            ax=self.axes["flows"],
            fig=self.figures["flows"],
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
        self.ani_3 = animation.FuncAnimation(
            fig=self.figures["flows"], func=flow, blit=True, interval=UPDATE_TIME,
        )

        delta_t = LivePlotHandler(
            ax=self.axes["delta_temperatures"],
            fig=self.figures["delta_temperatures"],
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

        self.ani_4 = animation.FuncAnimation(
            fig=self.figures["delta_temperatures"],
            func=delta_t,
            blit=True,
            interval=UPDATE_TIME,
        )

        pwm = LivePlotHandler(
            ax=self.axes["PWM"],
            fig=self.figures["PWM"],
            title="Power",
            ylabel="PWM",
            ylims=(0, 1),
            signal_buffers=[self.setup.measurement_buffer["PWM"]],
            time_buffer=self.setup.measurement_buffer["Time"],
            line_styles=["-k"],
            legend_entries=["PWM Output"],
            interval=self.setup.interval_s,
        )
        self.ani_5 = animation.FuncAnimation(
            fig=self.figures["PWM"], func=pwm, blit=True, interval=UPDATE_TIME,
        )
