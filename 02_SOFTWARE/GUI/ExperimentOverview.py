# The code for changing pages was derived from: http://stackoverflow.com/questions/7546050/switch-between-two-frames-in-tkinter
# License: http://creativecommons.org/licenses/by-sa/3.0/
from Utility.MeasurementBuffer import MeasurementBuffer
import matplotlib

matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot
import matplotlib.animation as animation
from matplotlib import style
import tkinter as tk
from tkinter import ttk
import numpy as np
from collections import namedtuple
from functools import partial

LARGE_FONT = ("Verdana", 12)
style.use("ggplot")

# Create plot
figure, axis = matplotlib.pyplot.subplots()
yList = [1, 2, 3, 4, 5, 6]
xList = [1, 5, 6, 3, 7, 2]
ln, = matplotlib.pyplot.plot([], [], 'ro')


def init_fig():
    """
    Initialize the figure
    """

    # Set the axis and plot titles
    axis.set_title('My fancy plot')
    axis.set_xlabel('Time [s]')
    axis.set_ylabel('Flow [slm]')

    # isSet axis limits
    axis.set_xlim(0, 10)
    axis.set_ylim(-20, 20)

    return ln,


def frame_iter():
    while True:
        yList[3] = yList[3] + np.random.rand() - np.random.rand()
        yield 1


def update_artists(frame):
    ln.set_data(xList, yList)
    return ln,


# Initialize artists
Artists = namedtuple("Artists", ("flow_line"))
artists = Artists(
    axis.plot([], [], animated=True)[0]
)

# Wrap functions
# init = partial(init_fig, fig=figure, ax=axis, artists=artists)
# step = frame_iter
# update = partial(update_artists, artists=artists)

measbuf = MeasurementBuffer(signals=['xList', 'yList'], buffer_length=10)
a = np.array(range(10))
b = a ** 2
measdict = {'xList': a, 'yList': b}
measbuf.update(measdict)


# class animate_plot():
#     def __init__(self):
#         self._line = None
#
#     def __call__(self, i):
#         yList[3] = yList[3] + 1
#         self._line = axis.plot(xList, yList)
#
# animate = animate_plot()


# def animate(i):
#     # yList = measbuf['xList'].data
#     # xList = measbuf['yList'].data
#     axis.clear()
#     yList[3] = yList[3] + 1
#     line = axis.plot(xList, yList, color='r')


class SeaofBTCapp(tk.Tk):

    def __init__(self, figure, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.figure = figure

        # tk.Tk.iconbitmap(self, default="clienticon.ico")
        tk.Tk.wm_title(self, "Sea of BTC client")

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (StartPage, PageOne, PageTwo, PageThree):
            frame = F(container, self, self.figure)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class StartPage(tk.Frame):

    def __init__(self, parent, controller, figure):
        self.figure = figure
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Start Page", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        button = ttk.Button(self, text="Visit Page 1",
                            command=lambda: controller.show_frame(PageOne))
        button.pack()

        button2 = ttk.Button(self, text="Visit Page 2",
                             command=lambda: controller.show_frame(PageTwo))
        button2.pack()

        button3 = ttk.Button(self, text="Graph Page",
                             command=lambda: controller.show_frame(PageThree))
        button3.pack()


class PageOne(tk.Frame):

    def __init__(self, parent, controller, figure):
        self.figure = figure
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Page One!!!", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        button1 = ttk.Button(self, text="Back to Home",
                             command=lambda: controller.show_frame(StartPage))
        button1.pack()

        button2 = ttk.Button(self, text="Page Two",
                             command=lambda: controller.show_frame(PageTwo))
        button2.pack()


class PageTwo(tk.Frame):

    def __init__(self, parent, controller, figure):
        self.figure = figure
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Page Two!!!", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        button1 = ttk.Button(self, text="Back to Home",
                             command=lambda: controller.show_frame(StartPage))
        button1.pack()

        button2 = ttk.Button(self, text="Page One",
                             command=lambda: controller.show_frame(PageOne))
        button2.pack()


class PageThree(tk.Frame):

    def __init__(self, parent, controller, figure):
        self.figure = figure
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Graph Page!", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        button1 = ttk.Button(self, text="Back to Home",
                             command=lambda: controller.show_frame(StartPage))
        button1.pack()

        canvas = FigureCanvasTkAgg(self.figure, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)


if __name__ == '__main__':
    # expview = ExperimentOverview(measurement_buffer=measbuf)
    # expview.run()

    app = SeaofBTCapp(figure=figure)
    ani = animation.FuncAnimation(fig=figure, func=update_artists, frames=frame_iter(), init_func=init_fig, blit=True)
    app.mainloop()
