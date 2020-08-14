from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from setup import Setup
import tkinter as tk
from tkinter import DISABLED, NORMAL, HORIZONTAL
from matplotlib import style
from functools import partial
import logging

logger = logging.getLogger("root")

LARGE_FONT = ("Verdana", 12)
MEDIUM_GRAY = "#d0d0d0"
WHITE = "#ffffff"
style.use("ggplot")
UPDATE_TIME = 100


class DiagnosticView(tk.Frame):
    def __init__(self, parent, controller, figures, setup: Setup):
        tk.Frame.__init__(self, master=parent, background="white")
        self.setup = setup

        #################
        # Label section #
        #################
        label_section = tk.Frame(master=self, background="white")
        label_section.grid(row=0, column=1, sticky="nwes")
        stop_go_section = tk.Frame(master=self, background="white")
        stop_go_section.grid(row=0, column=0, sticky="nwes")
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
        plotting_section.columnconfigure(2, weight=1)

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

        canvas_pid = FigureCanvasTkAgg(figures["pid_components"], plotting_section)
        canvas_pid.draw()
        canvas_pid.get_tk_widget().grid(column=2, row=0, sticky="sewn")

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

        def start_stop_measurement(setup=setup):
            if stop_measurement_button["text"] == "Stop":
                stop_measurement_button["text"] = "Start"
                setup.stop_measurement_thread()
            elif stop_measurement_button["text"] == "Start":
                stop_measurement_button["text"] = "Stop"
                setup.start_measurement_thread()
            else:
                raise RuntimeError('Invalid button state!')

        stop_measurement_button = tk.Button(
            master=stop_go_section,
            text='Stop',
            command=partial(start_stop_measurement, setup=self.setup)
        )
        stop_measurement_button.pack(side="top", padx=10, pady=10)

        self.power_scale = tk.Scale(
            master=self.power_section,
            from_=0,
            to=1,
            label="Power",
            background="white",
            resolution=0.01,
            showvalue=True,
            orient=HORIZONTAL,
            tickinterval=1 / 2,
            command=self.setup.wrap_set_pwm,
            length=100,
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
            tickinterval=1 / 2,
            command=self.setup.set_Kp,
            length=100,
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
            tickinterval=0.2 / 2,
            command=self.setup.set_Ki,
            length=100,
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
            tickinterval=10 / 2,
            command=self.setup.set_Kd,
            length=100,
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
            tickinterval=20 / 2,
            command=self.setup.set_setpoint,
            length=100,
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
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=100)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

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
