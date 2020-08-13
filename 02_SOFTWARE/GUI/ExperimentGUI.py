from setup import Setup
from GUI.Pages.Common import *
from GUI.LivePlot import LivePlot
from GUI.Pages.DiagnosticView import DiagnosticView
import logging


logger = logging.getLogger("root")


class TkGUI(tk.Tk):
    def __init__(self, setup: Setup, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.wm_title("Mass Flow Measurement")
        self.iconbitmap("GUI/icon.ico")

        self.setup = setup

        # Set up figures and axes
        self.figures = {}
        self.axes = {}
        self.live_plots = {}
        self.animations = {}
        self.figures_and_animations()

        # container = tk.Frame(self)
        container = ttk.Notebook(self, style="TNotebook")
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {
            StartPage: StartPage(parent=container, controller=self),
            DiagnosticView: DiagnosticView(
                parent=container, figures=self.figures, setup=setup
            ),
            # PWMSettingTraining: PWMSettingTraining(
            #    parent=container,
            #    controller=self,
            #    figure=self.figures["delta_temperatures"],
            #    setup=setup,
            # ),
        }

        for F in self.frames.values():
            F.grid(row=0, column=0, sticky="nsew")
            container.add(F, text=str(F))

        self.show_frame(StartPage)
        self.run()

    def figures_and_animations(self):
        # Set up figures and axes
        self.figures = {
            "temperatures": None,
            "flows": None,
            "delta_temperatures": None,
            "pwm": None,
            "pid": None,
        }
        self.axes = deepcopy(self.figures)
        for figure_name in self.figures.keys():
            fig, ax = plt.subplots()
            self.figures[figure_name] = fig
            self.axes[figure_name] = ax

        # Set up live plots
        self.live_plots["pid"] = LivePlot(
            ax=self.axes["pid"],
            fig=self.figures["pid"],
            title="PID Components",
            ylabel="Gain []",
            ylims=(-2, 2),
            signal_buffers=[
                self.setup.measurement_buffer["Controller Output P"],
                self.setup.measurement_buffer["Controller Output I"],
                self.setup.measurement_buffer["Controller Output D"],
            ],
            time_buffer=self.setup.measurement_buffer["Time"],
            line_styles=["b-", "r-", "g-"],
            legend_entries=["P", "I", "D"],
            interval=self.setup.interval_s,
        )

        self.live_plots["temperatures"] = LivePlot(
            ax=self.axes["temperatures"],
            fig=self.figures["temperatures"],
            title="Temperatures",
            ylabel="Temperature [deg C]",
            ylims=(20, 40),
            signal_buffers=[
                self.setup.measurement_buffer["Temperature 1"],
                self.setup.measurement_buffer["Temperature 2"],
            ],
            time_buffer=self.setup.measurement_buffer["Time"],
            line_styles=["b-", "k-"],
            legend_entries=["T1", "T2"],
            interval=self.setup.interval_s,
        )

        self.live_plots["flows"] = LivePlot(
            ax=self.axes["flows"],
            fig=self.figures["flows"],
            title="Flow",
            ylabel="Flow [slm]",
            ylims=(0, 100),
            signal_buffers=[
                self.setup.measurement_buffer["Flow"],
                self.setup.measurement_buffer["Flow Estimate"],
            ],
            time_buffer=self.setup.measurement_buffer["Time"],
            line_styles=["b-", "k-"],
            legend_entries=["SFM", "Estimate"],
            interval=self.setup.interval_s,
        )

        self.live_plots["delta_temperatures"] = LivePlot(
            ax=self.axes["delta_temperatures"],
            fig=self.figures["delta_temperatures"],
            title="Temperature Difference",
            ylabel="dT [deg C]",
            ylims=(0, 20),
            signal_buffers=[
                self.setup.measurement_buffer["Temperature Difference"],
                self.setup.measurement_buffer["Target Delta T"],
            ],
            time_buffer=self.setup.measurement_buffer["Time"],
            line_styles=["k-", "r-"],
            legend_entries=["\Delta T", "Target \Delta T"],
            interval=self.setup.interval_s,
        )

        self.live_plots["pwm"] = LivePlot(
            ax=self.axes["pwm"],
            fig=self.figures["pwm"],
            title="Power",
            ylabel="PWM",
            ylims=(0, 1),
            signal_buffers=[self.setup.measurement_buffer["PWM"]],
            time_buffer=self.setup.measurement_buffer["Time"],
            line_styles=["-k"],
            legend_entries=["PWM Output"],
            interval=self.setup.interval_s,
        )

        # Set up animations
        for key in self.figures.keys():
            time.sleep(0.005)
            self.animations[key] = animation.FuncAnimation(
                fig=self.figures[key],
                func=self.live_plots[key],
                blit=True,
                interval=UPDATE_TIME,
            )

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


class PageTwo(tk.Frame):
    def __init__(self, parent, controller, figure):
        self.figure = figure
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Page Two!!!", font=LARGE_FONT)
        label.pack(pady=10, padx=10)


class PWMSettingTraining(tk.Frame):
    def __init__(self, parent, controller, figure, setup):
        self.figure = figure
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Graph Page!", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        canvas = FigureCanvasTkAgg(self.figure, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        toolbar.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.power_scale = tk.Scale(
            master=self,
            from_=0,
            to=1,
            label="Power",
            background="white",
            resolution=0.01,
            showvalue=True,
            orient=HORIZONTAL,
            tickinterval=1 / 5.0,
            command=setup.wrap_set_pwm,
            length=400,
        )
        self.power_scale.set(0)
        self.power_scale.pack(side="top", padx=10, pady=10)

        def start_stop_measurement(setup=setup):
            if stop_measurement_button["text"] == "Stop":
                stop_measurement_button["text"] = "Start"
                setup.stop_measurement_thread()
            elif stop_measurement_button["text"] == "Start":
                stop_measurement_button["text"] = "Stop"
                setup.start_measurement_thread()
            else:
                raise RuntimeError("Invalid button state!")

        stop_measurement_button = tk.Button(
            master=self,
            text="Stop",
            command=partial(start_stop_measurement, setup=setup),
        )
        stop_measurement_button.pack(side="top", padx=10, pady=10)
