from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from setup import Setup
import tkinter as tk
from tkinter import DISABLED, NORMAL, HORIZONTAL
from tkinter import ttk
from matplotlib import style
from tkinter import messagebox
from functools import partial

LARGE_FONT = ("Verdana", 12)
MEDIUM_GRAY = "#d0d0d0"
WHITE = "#ffffff"
style.use("ggplot")


class TkGUI(tk.Tk):
    def __init__(self, figures, setup: Setup, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.figures = figures

        self.wm_title("Mass Flow Measurement")
        self.iconbitmap('GUI/icon.ico')


        # container = tk.Frame(self)
        container = ttk.Notebook(self, style="TNotebook")
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {
            StartPage: StartPage(parent=container, controller=self),
            DiagnosticView: DiagnosticView(
                parent=container, controller=self, figures=self.figures, setup=setup
            ),
            PageThree: PageThree(
                parent=container, controller=self, figure=self.figures["graph"]
            ),
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
        tk.Frame.__init__(self, master=parent, background="white")
        self.setup = setup

        #################
        # Label section #
        #################
        label_section = tk.Frame(master=self, background="white")
        label_section.grid(row=0, column=0, columnspan=2, sticky="nwes")
        label = tk.Label(
            label_section, text="Diagnostic View", font=LARGE_FONT, background="white"
        )
        label.pack(pady=10, padx=10)

        ####################
        # Plotting section #
        ####################
        plotting_section = tk.Frame(master=self, background="white")
        plotting_section.grid(row=1, column=1, sticky="se")
        plotting_section.rowconfigure(0, weight=1)
        plotting_section.rowconfigure(1, weight=1)
        plotting_section.columnconfigure(0, weight=1)
        plotting_section.columnconfigure(1, weight=1)

        canvas_temp = FigureCanvasTkAgg(
            figures["diagnostic_temperatures"], plotting_section
        )
        canvas_temp.draw()
        canvas_temp.get_tk_widget().grid(column=0, row=0, sticky="sewn")

        canvas_flow = FigureCanvasTkAgg(figures["diagnostic_flows"], plotting_section)
        canvas_flow.draw()
        canvas_flow.get_tk_widget().grid(column=1, row=0, sticky="sewn")

        canvas_d_temp = FigureCanvasTkAgg(
            figures["diagnostic_delta_temperatures"], plotting_section
        )
        canvas_d_temp.draw()
        canvas_d_temp.get_tk_widget().grid(column=0, row=1, sticky="sewn")

        canvas_pwm = FigureCanvasTkAgg(figures["diagnostic_PWM"], plotting_section)
        canvas_pwm.draw()
        canvas_pwm.get_tk_widget().grid(column=1, row=1, sticky="sewn")

        #######################
        # Interactive section #
        #######################
        self.interactive_section = tk.Frame(master=self, background="white")
        self.interactive_section.grid(row=1, column=0, padx=10, pady=10)
        self.mode_selection_section = tk.LabelFrame(
            master=self.interactive_section, background="white", text="Mode selection"
        )
        self.mode_selection_section.grid(row=0, column=0, padx=10, pady=10)
        self.power_section = tk.LabelFrame(
            master=self.interactive_section, background="white", text="PWM Setting"
        )
        self.power_section.grid(row=1, padx=10, pady=10)
        self.pid_section = tk.LabelFrame(
            master=self.interactive_section, background="white", text="PID Settings"
        )
        self.pid_section.grid(row=2, padx=10, pady=10)
        self.setpoint_section = tk.LabelFrame(
            master=self.interactive_section, background="white", text="Setpoint Setting"
        )
        self.setpoint_section.grid(row=3, padx=10, pady=10)
        self.interactive_section.rowconfigure(0, weight=1)
        self.interactive_section.rowconfigure(1, weight=1)
        self.interactive_section.rowconfigure(2, weight=1)
        self.interactive_section.rowconfigure(3, weight=1)

        self.power_scale = tk.Scale(
            master=self.power_section,
            from_=0,
            to=1,
            label="Power",
            background="white",
            resolution=0.01,
            showvalue=True,
            orient=HORIZONTAL,
            tickinterval=1 / 5.0,
            command=self.setup.wrap_set_pwm,
            length=400,
        )
        self.power_scale.set(0)
        self.power_scale.pack(side="top", padx=10, pady=10)

        self.P_scale = tk.Scale(
            master=self.pid_section,
            from_=0,
            to=1,
            label="P",
            background="white",
            resolution=0.01,
            showvalue=True,
            orient=HORIZONTAL,
            tickinterval=1 / 5,
            command=self.setup.set_Kp,
            length=400,
        )
        self.P_scale.set(self.setup.controller.Kp)
        self.P_scale.pack(side="top", padx=10, pady=10)

        self.I_scale = tk.Scale(
            master=self.pid_section,
            from_=0,
            to=0.2,
            label="I",
            background="white",
            resolution=0.01,
            showvalue=True,
            orient=HORIZONTAL,
            tickinterval=0.2 / 5,
            command=self.setup.set_Ki,
            length=400,
        )
        self.I_scale.set(self.setup.controller.Ki)
        self.I_scale.pack(side="top", padx=10, pady=10)

        self.D_scale = tk.Scale(
            master=self.pid_section,
            from_=0,
            to=10,
            label="D",
            background="white",
            resolution=0.1,
            showvalue=True,
            orient=HORIZONTAL,
            tickinterval=10 / 5,
            command=self.setup.set_Kd,
            length=400,
        )
        self.D_scale.set(self.setup.controller.Kd)
        self.D_scale.pack(side="top", padx=10, pady=10)

        self.Setpoint_scale = tk.Scale(
            master=self.setpoint_section,
            from_=0,
            to=20,
            label="Setpoint",
            background="white",
            resolution=1,
            showvalue=True,
            orient=HORIZONTAL,
            tickinterval=20 / 5,
            command=self.setup.set_setpoint,
            length=400,
        )
        self.Setpoint_scale.set(10)
        self.Setpoint_scale.pack(side="top", padx=10, pady=10)

        self.mode_var = tk.StringVar(self.interactive_section, "Set PWM")
        self.mode_check()
        set_power_switch = tk.Radiobutton(
            master=self.mode_selection_section,
            text="Set power",
            variable=self.mode_var,
            value="Set PWM",
            command=partial(self.mode_check),
        )
        set_power_switch.grid(column=0, row=0, padx=10, pady=10)
        set_pid_switch = tk.Radiobutton(
            master=self.mode_selection_section,
            text="Set PID",
            variable=self.mode_var,
            value="Set PID",
            command=partial(self.mode_check),
        )
        set_pid_switch.grid(column=1, row=0, padx=10, pady=10)

        # configure weighting of rows and columns upon resizing
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=3)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=7)

    def mode_check(self):
        if self.mode_var.get() in "Set PWM":
            for widget in self.power_section.winfo_children():
                self.enable_widget(widget)
            for widget in self.pid_section.winfo_children():
                self.disable_widget(widget)
            for widget in self.setpoint_section.winfo_children():
                self.disable_widget(widget)

            self.power_section.config(background=WHITE)
            self.pid_section.config(background=MEDIUM_GRAY)
            self.setpoint_section.config(background=MEDIUM_GRAY)

            self.setup.start_direct_power_setting()

        elif self.mode_var.get() in "Set PID":
            for widget in self.power_section.winfo_children():
                self.disable_widget(widget)
            for widget in self.pid_section.winfo_children():
                self.enable_widget(widget)
            for widget in self.setpoint_section.winfo_children():
                self.enable_widget(widget)

            self.power_section.config(background=MEDIUM_GRAY)
            self.pid_section.config(background="white")
            self.setpoint_section.config(background="white")

            self.setup.start_pid_controller(setpoint=10)

    @staticmethod
    def enable_widget(widget):
        widget.config(state=NORMAL, takefocus=1, background=WHITE)

    @staticmethod
    def disable_widget(widget):
        widget.config(state=DISABLED, takefocus=0, background=MEDIUM_GRAY)


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
