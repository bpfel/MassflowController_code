from GUI.Pages import TkGUI
from setup import Setup
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from copy import deepcopy
import logging

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

        pid = LivePlot(
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

        temp = LivePlot(
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

        flow = LivePlot(
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

        delta_t = LivePlot(
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

        pwm = LivePlot(
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


class LivePlot:
    def __init__(
            self,
            ax,
            fig,
            title,
            ylabel,
            ylims,
            signal_buffers,
            time_buffer,
            line_styles,
            legend_entries,
            interval,
    ):
        # Check input validity
        if len(signal_buffers) != len(line_styles) != len(legend_entries):
            raise AttributeError(
                "Number of signal buffers must be equal to number of line styles and number of legend entries."
            )
        # Set up line artists
        self.lines = []
        for line_style, legend_entry in zip(line_styles, legend_entries):
            (line,) = ax.plot([], [], line_style, label=legend_entry)
            self.lines.append(line)
        # Register members
        self.axis = ax
        self.interval = interval
        self.time_buffer = time_buffer
        self.signal_buffers = signal_buffers

        # Set the axis and plot titles
        self.axis.set_title(title)
        self.axis.set_xlabel("Time [s]")
        self.axis.set_ylabel(ylabel)

        # Set axis limits
        self.axis.set_xlim(0, self.interval)
        self.axis.set_ylim(ylims)

        # Set up the legend
        self.leg = fig.legend(
            handles=self.lines, loc="upper right", bbox_to_anchor=(0.9, 0.88)
        )

        # Counter for missing values
        self._missing_values = 0

    def __call__(self, i):
        if i == 0:
            for line in self.lines:
                line.set_data([], [])
            return self.lines
        if self.time_buffer:
            # Shift time such that the most up-to-date measurement is at the left of the plot
            t = np.array(self.time_buffer) - self.time_buffer[-1] + self.interval
            # Select only times that lie within the specified interval
            chosen_indices = t >= 0
            t_chosen = t[chosen_indices]
            # Go through all lines, draw the data, but only for the selected indices
            for line, signal_buffer in zip(self.lines, self.signal_buffers):
                line.set_data(t_chosen, np.array(signal_buffer)[chosen_indices])
        else:
            if self._missing_values < 10:
                self._missing_values += 1
            else:
                logger.warning("Empty measurement buffer!")
                self._missing_values = 0

        return self.lines

    def resize_yaxis(self):
        self.axis.set_ylim(auto=True)
