from tkinter import DISABLED, NORMAL, HORIZONTAL
from tkinter import ttk
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import tkinter as tk
from tkinter import messagebox
from functools import partial
from copy import deepcopy
import time
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

matplotlib.use("TkAgg")
style.use("ggplot")
LARGE_FONT = ("Verdana", 12)
MEDIUM_GRAY = "#d0d0d0"
WHITE = "#ffffff"
UPDATE_TIME = 100
