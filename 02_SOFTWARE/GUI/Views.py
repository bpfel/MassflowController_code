from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import tkinter as tk
from tkinter import DISABLED, NORMAL, HORIZONTAL
from functools import partial
from abc import abstractmethod

LARGE_FONT = ("Verdana", 12)
MEDIUM_GRAY = "#d0d0d0"
WHITE = "#ffffff"


class View(object):
    def __init__(self, master, figures, setup):
        self.master = master
        self.figures = figures
        self.setup = setup
        self.title = None

    @abstractmethod
    def load_widgets(self):
        pass

    @abstractmethod
    def destroy_widgets(self):
        pass


class DiagnosticView(View):
    def __init__(self, master, figures, setup):
        super(DiagnosticView, self).__init__(
            master=master, figures=figures, setup=setup
        )
        self.mode_var = tk.StringVar(
            master=master, value="Set PWM"
        )  # States: "Set PWM", "Set PID"
        self.title = "Diagnostic View"

    def load_widgets(self):
        ####################
        # Plotting section #
        ####################
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)
        self.master.columnconfigure(1, weight=1)
        plotting_section = tk.Frame(master=self.master, background="white")
        plotting_section.grid(row=0, column=1, sticky="se")
        plotting_section.rowconfigure(0, weight=1)
        plotting_section.rowconfigure(1, weight=1)
        plotting_section.columnconfigure(0, weight=1)
        plotting_section.columnconfigure(1, weight=1)
        plotting_section.columnconfigure(2, weight=1)

        # Necessary to make sure later figures are plotted correctly
        FigureCanvasTkAgg(self.figures["dummy"], plotting_section).draw()

        canvas_flow = FigureCanvasTkAgg(self.figures["flows"], plotting_section)
        canvas_flow.draw()
        canvas_flow.get_tk_widget().grid(column=1, row=0, sticky="sewn")

        canvas_temp = FigureCanvasTkAgg(self.figures["temperatures"], plotting_section)
        canvas_temp.draw()
        canvas_temp.get_tk_widget().grid(column=0, row=0, sticky="sewn")

        canvas_d_temp = FigureCanvasTkAgg(
            self.figures["delta_temperatures"], plotting_section
        )
        canvas_d_temp.draw()
        canvas_d_temp.get_tk_widget().grid(column=0, row=1, sticky="sewn")

        canvas_pwm = FigureCanvasTkAgg(self.figures["PWM"], plotting_section)
        canvas_pwm.draw()
        canvas_pwm.get_tk_widget().grid(column=2, row=1, sticky="sewn")

        canvas_pid = FigureCanvasTkAgg(self.figures["pid_components"], plotting_section)
        canvas_pid.draw()
        canvas_pid.get_tk_widget().grid(column=1, row=1, sticky="sewn")

        for fig in self.figures.values():
            fig.tight_layout()

        #######################
        # Interactive section #
        #######################
        interactive_section = tk.Frame(master=self.master, background="white")
        interactive_section.grid(row=0, column=0, padx=10, pady=10)
        mode_selection_section = tk.LabelFrame(
            master=interactive_section, background="white", text="Mode selection"
        )
        mode_selection_section.grid(row=0, column=0, padx=10, pady=10)
        power_section = tk.LabelFrame(
            master=interactive_section, background="white", text="PWM Setting"
        )
        power_section.grid(row=1, padx=10, pady=10)
        pid_section = tk.LabelFrame(
            master=interactive_section, background="white", text="PID Settings"
        )
        pid_section.grid(row=2, padx=10, pady=10)
        setpoint_section = tk.LabelFrame(
            master=interactive_section, background="white", text="Setpoint Setting"
        )
        setpoint_section.grid(row=3, padx=10, pady=10)
        interactive_section.rowconfigure(0, weight=1)
        interactive_section.rowconfigure(1, weight=1)
        interactive_section.rowconfigure(2, weight=1)
        interactive_section.rowconfigure(3, weight=1)

        power_scale = tk.Scale(
            master=power_section,
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
        power_scale.set(0)
        power_scale.pack(side="top", padx=10, pady=10)

        P_scale = tk.Scale(
            master=pid_section,
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
        P_scale.set(self.setup.controller.Kp)
        P_scale.pack(side="top", padx=10, pady=10)

        self.I_scale = tk.Scale(
            master=pid_section,
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
            master=pid_section,
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
            master=setpoint_section,
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

        self.mode_check(
            power_section=power_section,
            pid_section=pid_section,
            setpoint_section=setpoint_section,
        )
        set_power_switch = tk.Radiobutton(
            master=mode_selection_section,
            text="Set power",
            variable=self.mode_var,
            value="Set PWM",
            command=partial(
                self.mode_check,
                power_section=power_section,
                pid_section=pid_section,
                setpoint_section=setpoint_section,
            ),
        )
        set_power_switch.grid(column=0, row=0, padx=10, pady=10)
        set_pid_switch = tk.Radiobutton(
            master=mode_selection_section,
            text="Set PID",
            variable=self.mode_var,
            value="Set PID",
            command=partial(
                self.mode_check,
                power_section=power_section,
                pid_section=pid_section,
                setpoint_section=setpoint_section,
            ),
        )
        set_pid_switch.grid(column=1, row=0, padx=10, pady=10)

    def destroy_widgets(self):
        for widget in self.master.winfo_children():
            widget.destroy()

    def mode_check(self, power_section, pid_section, setpoint_section):
        if self.mode_var.get() in "Set PWM":
            for widget in power_section.winfo_children():
                self.enable_widget(widget)
            for widget in pid_section.winfo_children():
                self.disable_widget(widget)
            for widget in setpoint_section.winfo_children():
                self.disable_widget(widget)

            power_section.config(background=WHITE)
            pid_section.config(background=MEDIUM_GRAY)
            setpoint_section.config(background=MEDIUM_GRAY)

            self.setup.start_direct_power_setting()

        elif self.mode_var.get() in "Set PID":
            for widget in power_section.winfo_children():
                self.disable_widget(widget)
            for widget in pid_section.winfo_children():
                self.enable_widget(widget)
            for widget in setpoint_section.winfo_children():
                self.enable_widget(widget)

            power_section.config(background=MEDIUM_GRAY)
            pid_section.config(background="white")
            setpoint_section.config(background="white")

            self.setup.start_pid_controller(setpoint=10)

    @staticmethod
    def enable_widget(widget):
        widget.config(state=NORMAL, takefocus=1, background=WHITE)

    @staticmethod
    def disable_widget(widget):
        widget.config(state=DISABLED, takefocus=0, background=MEDIUM_GRAY)


class PWMSettingTrainingView(View):
    def __init__(self, master, figures, setup):
        super(PWMSettingTrainingView, self).__init__(
            master=master, figures=figures, setup=setup
        )
        self.title = "Direct Power Setting"

    def load_widgets(self):
        ####################
        # Plotting Section #
        ####################
        plotting_section = tk.Frame(master=self.master, background=WHITE)
        plotting_section.grid(row=0, column=1)
        plotting_section.rowconfigure(0, weight=1)
        plotting_section.rowconfigure(1, weight=1)
        plotting_section.columnconfigure(0, weight=1)

        # Necessary to make sure later figures are plotted correctly
        FigureCanvasTkAgg(self.figures["dummy"], plotting_section).draw()

        canvas_d_temp = FigureCanvasTkAgg(
            self.figures["delta_temperatures"], plotting_section
        )
        canvas_d_temp.draw()
        canvas_d_temp.get_tk_widget().grid(column=0, row=0, sticky="sewn")

        canvas_pwm = FigureCanvasTkAgg(self.figures["PWM"], plotting_section)
        canvas_pwm.draw()
        canvas_pwm.get_tk_widget().grid(column=0, row=1, sticky="sewn")

        #######################
        # Interactive section #
        #######################
        interactive_section = tk.Frame(master=self.master, background=WHITE)
        interactive_section.grid(row=0, column=0, padx=10, pady=10)

        power_scale = tk.Scale(
            master=interactive_section,
            from_=0,
            to=1,
            label="Power",
            background="white",
            resolution=0.01,
            showvalue=True,
            orient=HORIZONTAL,
            tickinterval=1 / 5,
            command=self.setup.wrap_set_pwm,
            length=400,
        )
        power_scale.set(0)
        power_scale.pack(side="top", padx=10, pady=10)

    def destroy_widgets(self):
        for widget in self.master.winfo_children():
            widget.destroy()
