from GUI.Pages import TkGUI
from setup import Setup
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from copy import deepcopy
from collections import deque
import time

matplotlib.use("TkAgg")


class ExperimentOverview():
    def __init__(self, setup: Setup):
        self.figures = {
            'diagnostic_temperatures': None,
            'diagnostic_flows': None,
            'diagnostic_delta_temperatures': None,
            'diagnostic_PWM': None,
            'graph': None,
        }
        self.axes = deepcopy(self.figures)
        self.setup = setup
        for figure_name in self.figures.keys():
            fig, ax = plt.subplots()
            self.figures[figure_name] = fig
            self.axes[figure_name] = ax
        self.app = TkGUI(figures=self.figures, setup=setup)

        temp = DoubleLiveMeasurement(ax=self.axes['diagnostic_temperatures'], title='Temperatures',
                                     ylabel='Temperature [deg C]', ylims=(20, 40),
                                     signal_buffer_one=setup.measurement_buffer['Temperature 1'],
                                     signal_buffer_two=setup.measurement_buffer['Temperature 2'],
                                     time_buffer=setup.measurement_buffer['Time'])
        self.ani_2 = animation.FuncAnimation(fig=self.figures['diagnostic_temperatures'], func=temp, blit=True,
                                             interval=100)

        flow = DoubleLiveMeasurement(ax=self.axes['diagnostic_flows'], title='Flow',
                                     ylabel='Flow [slm]', ylims=(0, 100),
                                     signal_buffer_one=setup.measurement_buffer['Flow'],
                                     signal_buffer_two=setup.measurement_buffer['Flow Estimate'],
                                     time_buffer=setup.measurement_buffer['Time'])
        self.ani_3 = animation.FuncAnimation(fig=self.figures['diagnostic_flows'], func=flow, blit=True, interval=100)

        delta_t = SingleLiveMeasurement(ax=self.axes['diagnostic_delta_temperatures'],
                                        title='Temperature Difference', ylabel='dT [deg C]', ylims=(0, 20),
                                        signal_buffer=setup.measurement_buffer['Temperature Difference'],
                                        time_buffer=setup.measurement_buffer['Time'])

        self.ani_4 = animation.FuncAnimation(fig=self.figures['diagnostic_delta_temperatures'], func=delta_t, blit=True,
                                             interval=100)

        pwm = SingleLiveMeasurement(ax=self.axes['diagnostic_PWM'], title='Power',
                                    ylabel='PWM', ylims=(0, 1),
                                    signal_buffer=setup.measurement_buffer['PWM'],
                                    time_buffer=setup.measurement_buffer['Time'])
        self.ani_5 = animation.FuncAnimation(fig=self.figures['diagnostic_PWM'], func=pwm, blit=True, interval=100)
        self.app.run()


class DoubleLiveMeasurement:
    def __init__(self, ax, title, ylabel, ylims, signal_buffer_one, signal_buffer_two, time_buffer):
        self.line_one, = ax.plot([], [], 'k-')
        self.line_two, = ax.plot([], [], 'b-')
        self.axis = ax
        self.time_buffer = time_buffer
        self.signal_buffer_one = signal_buffer_one
        self.signal_buffer_two = signal_buffer_two

        # Set the axis and plot titles
        self.axis.set_title(title)
        self.axis.set_xlabel('Time [s]')
        self.axis.set_ylabel(ylabel)

        # Set axis limits
        self.axis.set_xlim(0, 20)
        self.axis.set_ylim(ylims)

    def __call__(self, i):
        if i == 0:
            self.line_one.set_data([], [])
            self.line_two.set_data([], [])
            return self.line_one, self.line_two,
        t = list(self.time_buffer)
        y_1 = list(self.signal_buffer_one)
        y_2 = list(self.signal_buffer_two)
        self.line_one.set_data(t, y_1)
        self.line_two.set_data(t, y_2)
        self.axis.set_xlim(min(t), max(t) + 1.0)
        return self.line_one, self.line_two,


class SingleLiveMeasurement:
    def __init__(self, ax, title, ylabel, ylims, signal_buffer, time_buffer):
        self.line, = ax.plot([], [], 'k-')
        self.axis = ax
        self.time_buffer = time_buffer
        self.signal_buffer = signal_buffer

        # Set the axis and plot titles
        self.axis.set_title(title)
        self.axis.set_xlabel('Time [s]')
        self.axis.set_ylabel(ylabel)

        # Set axis limits
        self.axis.set_xlim(0, 20)
        self.axis.set_ylim(ylims)

    def __call__(self, i):
        if i == 0:
            self.line.set_data([], [])
            return self.line,
        t = list(self.time_buffer)
        y = list(self.signal_buffer)
        self.line.set_data(t, y)
        self.axis.set_xlim(min(t), max(t) + 1.0)
        return self.line,


class SingleDummyLiveMeasurement:
    def __init__(self, ax, title, ylabel, ylims):
        self.line, = ax.plot([], [], 'k-')
        self.axis = ax
        self.xList = deque(maxlen=50)
        self.yList = deque(maxlen=50)
        self.initial_time = time.time()
        self.xList.append(time.time() - self.initial_time)
        self.yList.append(0)

        # Set the axis and plot titles
        self.axis.set_title(title)
        self.axis.set_xlabel('Time [s]')
        self.axis.set_ylabel(ylabel)

        # Set axis limits
        self.axis.set_xlim(0, 20)
        self.axis.set_ylim(ylims)

        # Set x axis tiks
        self.axis.xticks(np.arange(0, 20, 1))

    def __call__(self, i):
        if i == 0:
            self.line.set_data([], [])
            return self.line,
        t = time.time()
        self.xList.append(t - self.initial_time)
        self.yList.append(np.random.rand() - np.random.rand())
        self.line.set_data(list(self.xList), list(self.yList))
        self.axis.set_xlim(min(self.xList), max(self.xList) + 1.0)
        return self.line,
