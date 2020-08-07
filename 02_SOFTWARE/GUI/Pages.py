from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from setup import Setup
import tkinter as tk
from tkinter import DISABLED, NORMAL, HORIZONTAL
from tkinter import ttk
from matplotlib import style
from tkinter import messagebox
from functools import partial

LARGE_FONT = ("Verdana", 12)
style.use("ggplot")


class Scale(tk.Scale):
    """a type of Scale where the left click is hijacked to work like a right click"""

    def __init__(self, master=None, **kwargs):
        tk.Scale.__init__(self, master, **kwargs)
        self.bind('<Button-1>', self.set_value)

    def set_value(self, event):
        self.event_generate('<Button-3>', x=event.x, y=event.y)
        return 'break'


class TkGUI(tk.Tk):

    def __init__(self, figures, setup: Setup, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.figures = figures

        tk.Tk.wm_title(self, "Mass Flow Measurement")

        # container = tk.Frame(self)
        container = ttk.Notebook(self, style="TNotebook")
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {
            StartPage: StartPage(parent=container, controller=self),
            DiagnosticView: DiagnosticView(parent=container, controller=self, figures=self.figures, setup=setup),
            PageThree: PageThree(parent=container, controller=self, figure=self.figures['graph']),
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


class DiagnosticView(tk.Frame):

    def __init__(self, parent, controller, figures, setup: Setup):
        tk.Frame.__init__(self, master=parent, background='white')
        self.setup = setup

        #################
        # Label section #
        #################
        label_section = tk.Frame(master=self, background='white')
        label_section.grid(row=0, column=0, columnspan=2, sticky='nwes')
        label = tk.Label(label_section, text="Diagnostic View", font=LARGE_FONT, background='white')
        label.pack(pady=10, padx=10)

        ####################
        # Plotting section #
        ####################
        plotting_section = tk.Frame(master=self, background='white')
        plotting_section.grid(row=1, column=1, sticky='se')
        plotting_section.rowconfigure(0, weight=1)
        plotting_section.rowconfigure(1, weight=1)
        plotting_section.columnconfigure(0, weight=1)
        plotting_section.columnconfigure(1, weight=1)

        canvas_temp = FigureCanvasTkAgg(figures['diagnostic_temperatures'], plotting_section)
        canvas_temp.draw()
        canvas_temp.get_tk_widget().grid(column=0, row=0, sticky='sewn')

        canvas_flow = FigureCanvasTkAgg(figures['diagnostic_flows'], plotting_section)
        canvas_flow.draw()
        canvas_flow.get_tk_widget().grid(column=1, row=0, sticky='sewn')

        canvas_d_temp = FigureCanvasTkAgg(figures['diagnostic_delta_temperatures'], plotting_section)
        canvas_d_temp.draw()
        canvas_d_temp.get_tk_widget().grid(column=0, row=1, sticky='sewn')

        canvas_pwm = FigureCanvasTkAgg(figures['diagnostic_PWM'], plotting_section)
        canvas_pwm.draw()
        canvas_pwm.get_tk_widget().grid(column=1, row=1, sticky='sewn')

        #######################
        # Interactive section #
        #######################
        interactive_section = tk.Frame(master=self, background='white')
        interactive_section.grid(row=1, column=0)
        power_section = tk.Frame(master=interactive_section, background='white')
        power_section.grid(row=0)
        pid_section = tk.Frame(master=interactive_section, background='white')
        pid_section.grid(row=1)
        interactive_section.rowconfigure(0, weight=1)
        interactive_section.rowconfigure(1, weight=1)

        self.P_scale = Scale(master=pid_section, from_=0, to=1.5, label='P', background='white',
                             resolution=0.01, showvalue=True, orient=HORIZONTAL, tickinterval=0.25,
                             command=self.setup.controller.set_k_p, length=400)
        self.P_scale.set(0)

        self.I_scale = Scale(master=pid_section, from_=0, to=0.2, label='I', background='white',
                             resolution=0.01, showvalue=True, orient=HORIZONTAL, tickinterval=0.25,
                             command=self.setup.controller.set_k_i, length=400)
        self.I_scale.set(0)

        self.D_scale = Scale(master=pid_section, from_=0, to=1, label='D', background='white',
                             resolution=0.01, showvalue=True, orient=HORIZONTAL, tickinterval=0.25,
                             command=self.setup.controller.set_k_d, length=400)
        self.D_scale.set(0)

        self.power_scale = Scale(master=power_section, from_=0, to=1, label='Power', background='white',
                                 resolution=0.01, showvalue=True, orient=HORIZONTAL, tickinterval=0.25,
                                 command=self.setup.wrap_set_pwm, length=400)
        self.power_scale.set(0)

        self.mode_var = tk.StringVar(interactive_section, 'Set PWM')
        self.mode_check()

        mode_switch = tk.Checkbutton(master=power_section, textvariable=self.mode_var,
                                     width=12, variable=self.mode_var, offvalue='Set PWM',
                                     onvalue='Set PID', indicator=False, command=partial(self.mode_check))
        mode_switch.pack(pady=10, padx=10)
        self.power_scale.pack(side='top', padx=10, pady=10)
        self.P_scale.pack(side='top', padx=10, pady=10)
        self.I_scale.pack(side='top', padx=10, pady=10)
        self.D_scale.pack(side='top', padx=10, pady=10)

        # configure weighting of rows and columns upon resizing
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=3)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=7)

    def mode_check(self):
        if self.mode_var.get() in 'Set PWM':
            self.power_scale.config(state=NORMAL, takefocus=1, background='#ffffff')
            self.P_scale.config(state=DISABLED, takefocus=0, background='#d0d0d0')
            self.I_scale.config(state=DISABLED, takefocus=0, background='#d0d0d0')
            self.D_scale.config(state=DISABLED, takefocus=0, background='#d0d0d0')
            self.setup.start_direct_power_setting()
        elif self.mode_var.get() in 'Set PID':
            self.power_scale.config(state=DISABLED, takefocus=0, background='#d0d0d0')
            self.P_scale.config(state=NORMAL, takefocus=1, background='#ffffff')
            self.I_scale.config(state=NORMAL, takefocus=1, background='#ffffff')
            self.D_scale.config(state=NORMAL, takefocus=1, background='#ffffff')
            self.setup.start_pid_controller(setpoint=10)


class PageTwo(tk.Frame):

    def __init__(self, parent, controller, figure):
        self.figure = figure
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Page Two!!!", font=LARGE_FONT)
        label.pack(pady=10, padx=10)


class PageThree(tk.Frame):

    def __init__(self, parent, controller, figure):
        self.figure = figure
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Graph Page!", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        canvas = FigureCanvasTkAgg(self.figure, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
