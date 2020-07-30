from Utility.MeasurementBuffer import MeasurementBuffer
from GUI.Pages import TkGUI
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

matplotlib.use("TkAgg")


class ExperimentOverview:
    def __init__(self):
        self.figure, self.axis = plt.subplots()
        self.app = TkGUI(figure=self.figure)

        ud = SingleLiveMeasurement(ax=self.axis)
        self.ani = animation.FuncAnimation(fig=self.figure, func=ud, blit=True)

        # Start the app
        self.app.mainloop()


class SingleLiveMeasurement:
    def __init__(self, ax):
        self.line, = ax.plot([], [], 'k-')
        self.axis = ax
        self.xList = [1, 2, 3, 4, 5, 6]
        self.yList = [1, 4, 2, 4, 6, 2]

        # Set the axis and plot titles
        self.axis.set_title('My fancy plot')
        self.axis.set_xlabel('Time [s]')
        self.axis.set_ylabel('Flow [slm]')

        # isSet axis limits
        self.axis.set_xlim(0, 10)
        self.axis.set_ylim(-20, 20)

    def __call__(self, i):
        if i == 0:
            self.line.set_data([], [])
            return self.line,
        self.yList[3] = self.yList[3] + np.random.rand() - np.random.rand()
        self.line.set_data(self.xList, self.yList)
        return self.line,


if __name__ == '__main__':
    expview = ExperimentOverview()
