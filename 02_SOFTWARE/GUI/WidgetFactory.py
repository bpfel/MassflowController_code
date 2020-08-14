from setup import Setup
import tkinter as tk
from tkinter import DISABLED, NORMAL, HORIZONTAL
from functools import partial
import logging
from matplotlib import style
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

from GUI.LivePlotHandler import LivePlotHandler

logger = logging.getLogger("root")

LARGE_FONT = ("Verdana", 12)
MEDIUM_GRAY = "#d0d0d0"
WHITE = "#ffffff"
style.use("ggplot")
UPDATE_TIME = 100


class WidgetFactory(object):
    def __init__(self, setup: Setup, initial_parent: tk.Frame, figures):
        # Allocating members
        self.setup = setup,
        self.initial_parent = initial_parent
        self.figures = figures
        self.plot_widgets = {}
        self.test_widgets = {}

        self.create_widgets()

    def create_widgets(self):
        for figure_name in self.figures.keys():
            self.plot_widgets[figure_name] = Plot(
                master=self.initial_parent,
                figure=self.figures[figure_name]
            )
        self.test_widgets["test"] = tk.Label(master=self.initial_parent, text="testlabel")
        self.test_widgets["test"].grid(row=1, column=1)


class Plot():
    def __init__(self, master, figure):
        self.figure = figure
        self.canvas = FigureCanvasTkAgg(figure, master)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0)
