from GUI.LivePlots import PlotWidgetFactory
from GUI.CustomWidgets.Widgets import *
import logging

logger = logging.getLogger("root")

INDEX_COMPETITION_WIDGET = 1


class ExperimentPage(QWidget):
    def __init__(self, setup, start_action, stop_action, name):
        super(ExperimentPage, self).__init__()
        self.setup = setup
        self.name = name
        self.mode = 0
        self.plot_widget_factory = PlotWidgetFactory(setup=setup)
        self.competition_widget = CompetitionWidget(
            setup=setup, start_action=start_action, stop_action=stop_action
        )
        self.vertical_layout_controls = QVBoxLayout()
        self.vertical_layout_plots = QVBoxLayout()
        self.vertical_layout_plots.setContentsMargins(10, 10, 10, 10)
        self.vertical_layout_controls.setContentsMargins(10, 10, 10, 10)
        self.horizontal_layout = QHBoxLayout()
        self.horizontal_layout.addLayout(self.vertical_layout_controls, 1)
        self.horizontal_layout.addLayout(self.vertical_layout_plots, 3)
        self.setLayout(self.horizontal_layout)

    def enter(self):
        NotImplementedError(
            "enter() sequence for page {} not implemented!".format(self.name)
        )

    def leave(self):
        if self.mode == 1:
            self.switch_to_normal_mode()
        self.leave_individual()

    def leave_individual(self):
        NotImplementedError(
            "leave_individual() sequence for page {} not implemented!".format(self.name)
        )

    def pause(self):
        NotImplementedError(
            "pause() sequence for page {} not implemented!".format(self.name)
        )

    def reset_plots(self):
        for i in range(self.vertical_layout_plots.count()):
            self.vertical_layout_plots.itemAt(i).widget().reset_plot_layout()

    def switch_to_competition_mode(self):
        self.mode = 1
        # Change plot behaviour
        delta_t_plot_widget = self.vertical_layout_plots.itemAt(0).widget()
        self.vertical_layout_plots.removeWidget(delta_t_plot_widget)
        delta_t_plot_widget.setVisible(False)
        del delta_t_plot_widget
        self.vertical_layout_plots.insertWidget(
            0, self.plot_widget_factory.delta_t_competition()
        )
        # Add competition_widget
        self.vertical_layout_controls.insertWidget(
            INDEX_COMPETITION_WIDGET, self.competition_widget
        )
        self.competition_widget.reset()
        self.competition_widget.setVisible(True)

    def switch_to_normal_mode(self):
        # Change plot behaviour
        self.mode = 0
        delta_t_plot_widget = self.vertical_layout_plots.itemAt(0).widget()
        self.vertical_layout_plots.removeWidget(delta_t_plot_widget)
        delta_t_plot_widget.setVisible(False)
        del delta_t_plot_widget
        self.vertical_layout_plots.insertWidget(0, self.plot_widget_factory.delta_t())
        # Remove counter widget
        self.vertical_layout_controls.removeWidget(self.competition_widget)
        self.competition_widget.setVisible(False)


class PWMSetting(ExperimentPage):
    def __init__(self, setup, start_action, stop_action):
        super(PWMSetting, self).__init__(
            setup=setup,
            start_action=start_action,
            stop_action=stop_action,
            name="PWM Setting Page",
        )
        # Create controls
        self.pwm = AnnotatedSlider(min=0, max=1, title="Heating Power")
        self.pwm.value = self.setup._current_pwm_value
        self.pwm.slider.valueChanged.connect(self.set_pwm_value)

        # Add widgets to layout
        self.vertical_layout_controls.addWidget(StatusWidget(setup=self.setup))
        self.vertical_layout_controls.addWidget(self.pwm)
        # Placeholder to prevent spreading of widgets across vertical space
        self.vertical_layout_controls.addWidget(QLabel(), 1)
        self.vertical_layout_plots.addWidget(self.plot_widget_factory.delta_t())
        self.vertical_layout_plots.addWidget(self.plot_widget_factory.power())

    def set_pwm_value(self):
        self.setup.wrap_set_pwm(value=self.pwm.value)

    def enter(self):
        self.setup.start_direct_power_setting()

    def leave_individual(self):
        self.setup.wrap_set_pwm(0)

    def pause(self):
        self.pwm.value = 0


class PIDSetting(ExperimentPage):
    def __init__(self, setup, start_action, stop_action):
        super(PIDSetting, self).__init__(
            setup=setup,
            start_action=start_action,
            stop_action=stop_action,
            name="PID Setting Page",
        )

        # Create controls
        self.p_gain = AnnotatedSlider(min=0, max=0.1, title="K_p")
        self.i_gain = AnnotatedSlider(min=0, max=0.1, title="K_i")
        self.d_gain = AnnotatedSlider(min=0, max=0.1, title="K_d")
        self.p_gain.value = 0.0
        self.i_gain.value = 0.0
        self.d_gain.value = 0.0
        self.p_gain.slider.valueChanged.connect(self.set_p_value)
        self.i_gain.slider.valueChanged.connect(self.set_i_value)
        self.d_gain.slider.valueChanged.connect(self.set_d_value)

        # Add widgets to layout
        self.vertical_layout_controls.addWidget(StatusWidget(setup=self.setup))
        self.vertical_layout_controls.addWidget(self.p_gain)
        self.vertical_layout_controls.addWidget(self.i_gain)
        self.vertical_layout_controls.addWidget(self.d_gain)
        # Placeholder to prevent spreading of widgets across vertical space
        self.vertical_layout_controls.addWidget(QLabel(), 1)
        self.vertical_layout_plots.addWidget(self.plot_widget_factory.delta_t())
        self.vertical_layout_plots.addWidget(self.plot_widget_factory.pid())

    def set_p_value(self):
        self.setup.set_Kp(self.p_gain.value)

    def set_i_value(self):
        self.setup.set_Ki(self.i_gain.value)

    def set_d_value(self):
        self.setup.set_Kd(self.d_gain.value)

    def enter(self):
        logger.info("Start PID controller")
        self.setup.start_pid_controller()

    def leave_individual(self):
        self.setup.set_Kp(0)
        self.setup.set_Ki(0)
        self.setup.set_Kd(0)

    def pause(self):
        pass
