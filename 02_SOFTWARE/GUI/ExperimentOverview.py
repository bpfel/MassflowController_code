from GUI.ExperimentGUI import TkGUI
from setup import Setup
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from copy import deepcopy
import logging
from GUI.LivePlotHandler import LivePlotHandler

logger = logging.getLogger("root")

matplotlib.use("TkAgg")
UPDATE_TIME = 100


class ExperimentOverview:
    def __init__(self, setup: Setup):
        self.figures = {
            "diagnostic_temperatures": None,
            "diagnostic_flows": None,
            "diagnostic_delta_temperatures": None,
            "diagnostic_PWM": None,
            "graph": None,
            "pid_components": None,
        }
        self.axes = deepcopy(self.figures)
        self.setup = setup
        for figure_name in self.figures.keys():
            fig, ax = plt.subplots()
            self.figures[figure_name] = fig
            self.axes[figure_name] = ax
        self.app = TkGUI(figures=self.figures, setup=setup)

        pid = LivePlotHandler(
            ax=self.axes["pid_components"],
            fig=self.figures["pid_components"],
            title="PID Components",
            ylabel="Gain []",
            ylims=(-2, 2),
            signal_buffers=[
                setup.measurement_buffer["Controller Output P"],
                setup.measurement_buffer["Controller Output I"],
                setup.measurement_buffer["Controller Output D"],
            ],
            time_buffer=setup.measurement_buffer["Time"],
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
            ax=self.axes["diagnostic_temperatures"],
            fig=self.figures["diagnostic_temperatures"],
            title="Temperatures",
            ylabel="Temperature [deg C]",
            ylims=(20, 40),
            signal_buffers=[
                setup.measurement_buffer["Temperature 1"],
                setup.measurement_buffer["Temperature 2"],
            ],
            time_buffer=setup.measurement_buffer["Time"],
            line_styles=["b-", "k-"],
            legend_entries=["T1", "T2"],
            interval=self.setup.interval_s,
        )
        self.ani_2 = animation.FuncAnimation(
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
                setup.measurement_buffer["Flow"],
                setup.measurement_buffer["Flow Estimate"],
            ],
            time_buffer=setup.measurement_buffer["Time"],
            line_styles=["b-", "k-"],
            legend_entries=["SFM", "Estimate"],
            interval=self.setup.interval_s,
        )
        self.ani_3 = animation.FuncAnimation(
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
                setup.measurement_buffer["Temperature Difference"],
                setup.measurement_buffer["Target Delta T"],
            ],
            time_buffer=setup.measurement_buffer["Time"],
            line_styles=["k-", "r-"],
            legend_entries=["\Delta T", "Target \Delta T"],
            interval=self.setup.interval_s,
        )

        self.ani_4 = animation.FuncAnimation(
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
            signal_buffers=[setup.measurement_buffer["PWM"]],
            time_buffer=setup.measurement_buffer["Time"],
            line_styles=["-k"],
            legend_entries=["PWM Output"],
            interval=self.setup.interval_s,
        )
        self.ani_5 = animation.FuncAnimation(
            fig=self.figures["diagnostic_PWM"],
            func=pwm,
            blit=True,
            interval=UPDATE_TIME,
        )
        self.app.run()


