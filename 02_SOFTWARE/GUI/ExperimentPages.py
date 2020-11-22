from GUI.CustomWidgets.LivePlots import PlotWidgetFactory
from GUI.CustomWidgets.Widgets import *
from setup import Setup
from typing import Callable
import logging

logger = logging.getLogger("root")

INDEX_COMPETITION_WIDGET = 1


class ExperimentPage(QWidget):
    """
    Base class for the different experiment views. Defines all interfaces with the main layout / the tool bar.

    :type setup: Setup
    :param setup: Instance of Setup to allow access to sensors and actuators.
    :type name: str
    :param name: Name of the inheriting experiment page.
    """

    def __init__(self, setup: Setup, name: str, ) -> None:
        super(ExperimentPage, self).__init__()
        self.setup = setup
        self.name = name
        self.competition_mode = False
        self.plot_widget_factory = PlotWidgetFactory(setup=setup)
        self.setup_basic_layout()

    def setup_basic_layout(self) -> None:
        """
        Defines the basic layout of an experiment page
        """
        self.vertical_layout_controls = QVBoxLayout()
        self.vertical_layout_plots = QVBoxLayout()
        self.vertical_layout_plots.setContentsMargins(10, 10, 10, 10)
        self.vertical_layout_controls.setContentsMargins(10, 10, 10, 10)
        self.horizontal_layout = QHBoxLayout()
        self.horizontal_layout.addLayout(self.vertical_layout_controls, 1)
        self.horizontal_layout.addLayout(self.vertical_layout_plots, 3)
        self.vertical_layout_title = QVBoxLayout()
        self.title_label = QLabel(self.name)
        self.title_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.vertical_layout_title.addWidget(self.title_label)
        self.vertical_layout_title.addLayout(self.horizontal_layout)
        self.setLayout(self.vertical_layout_title)

    def enter(self) -> None:
        """
        Defines the actions to be taken when this page is loaded. Split into a general set of actions and an
           individual set defined by the inheriting class.
        """
        self.title_label.setText(self.name)
        self.enter_individual()

    def enter_individual(self) -> None:
        """
        Allows to implement a set of individual actions to be taken when the inheriting page is loaded.
        """
        NotImplementedError(
            "enter_individual() sequence for page {} not implemented!".format(self.name)
        )

    def leave(self) -> None:
        """
        Defines the actions to be taken when this page is left. Split into a general set of actions and an
           individual set defined by the inheriting class.
        """
        if self.competition_mode:
            self.switch_to_normal_mode()
        self.leave_individual()

    def leave_individual(self) -> None:
        """
        Allows to implement a set of individual actions to be taken when the inheriting page is left.
        """
        NotImplementedError(
            "leave_individual() sequence for page {} not implemented!".format(self.name)
        )

    def reset_plots(self) -> None:
        """
        Resets all plots within the plot layout of the inheriting page to their initial view.
        """
        for i in range(self.vertical_layout_plots.count()):
            self.vertical_layout_plots.itemAt(i).widget().reset_plot_layout()

    def switch_to_competition_mode(self) -> None:
        """
        Loads the competition widget and changes the behaviour of the temperature difference plot to show
        the integral of the current control error.
        """
        self.competition_mode = True
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

    def switch_to_normal_mode(self) -> None:
        """
        Unloads the competition widget and changes the behaviour of the temperature difference plot back to normal.
        """
        # Change plot behaviour
        self.competition_mode = False
        delta_t_plot_widget = self.vertical_layout_plots.itemAt(0).widget()
        self.vertical_layout_plots.removeWidget(delta_t_plot_widget)
        delta_t_plot_widget.setVisible(False)
        del delta_t_plot_widget
        self.vertical_layout_plots.insertWidget(0, self.plot_widget_factory.delta_t())
        # Remove counter widget
        self.vertical_layout_controls.removeWidget(self.competition_widget)
        self.competition_widget.setVisible(False)

    def desired_pwm_output(self):
        """
        Allows each inheriting page to return the current desired PWM output, such that the actual output can be
           updated.
        """
        raise NotImplementedError(
            "'desired_pwm_output' not implemented for page {}!".format(self.name)
        )


class PWMSetting(ExperimentPage):
    """
    First experiment page allowing the students to set the current pwm output manually and attempt to control
       the temperature difference themselves.
    """

    def __init__(
            self, setup, start_recording_action, stop_recording_action, enable_output_action
    ):
        self.competition_widget = CompetitionReferenceTrackingWidget(
            setup=setup,
            start_recording_action=start_recording_action,
            stop_recording_action=stop_recording_action,
            enable_output_action=enable_output_action,
        )
        super(PWMSetting, self).__init__(
            setup=setup,
            name="Experiment Page 1: Human in the Loop",
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
        self.setup.set_pwm(value=self.pwm.value)

    def enter_individual(self):
        self.setup.start_direct_power_setting()

    def leave_individual(self):
        self.setup.set_pwm(0)

    def desired_pwm_output(self):
        return self.pwm.value


class PIDSetting(ExperimentPage):
    """
    Second experiment page allowing the students to define the gains of a PID controller and testing it on the system.
    """

    def __init__(
            self, setup, start_recording_action, stop_recording_action, enable_output_action, set_flow_action
    ):
        # Create competition widget
        self.competition_widget = CompetitionDisturbanceRejectionWidget(
            setup=setup,
            start_recording_action=start_recording_action,
            stop_recording_action=stop_recording_action,
            enable_output_action=enable_output_action,
            set_flow_action=set_flow_action
        )
        super(PIDSetting, self).__init__(
            setup=setup,
            name="Experiment Page 2: PID Controller",
        )

        # Create controls
        self.p_gain = AnnotatedSlider(min=0, max=0.3, title="K_p")
        self.i_gain = AnnotatedSlider(min=0, max=0.3, title="K_i")
        self.d_gain = AnnotatedSlider(min=0, max=0.3, title="K_d")
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
        self.setup.set_kp(self.p_gain.value)

    def set_i_value(self):
        self.setup.set_ki(self.i_gain.value)

    def set_d_value(self):
        self.setup.set_kd(self.d_gain.value)

    def enter_individual(self):
        self.setup.start_pid_controller()
        self.p_gain.value = self.setup.controller.Kp
        self.i_gain.value = self.setup.controller.Ki
        self.d_gain.value = self.setup.controller.Kd
        self.set_p_value()
        self.set_i_value()
        self.set_d_value()

    def leave_individual(self):
        pass

    def desired_pwm_output(self):
        return 0


class MassFlowEstimation(ExperimentPage):
    """
    Third experiment page allowing the students to analyze the performance of the mass flow estimation

    This page assumes that a working controller is in place and hands over mass flow control to the user
    """

    def __init__(
            self, setup, enable_competition_mode, disable_competition_mode,
            enable_massflow_setting, disable_massflow_setting
    ):
        self.enable_competition_mode = enable_competition_mode
        self.disable_competition_mode = disable_competition_mode
        self.enable_massflow_setting = enable_massflow_setting
        self.disable_massflow_setting = disable_massflow_setting

        super(MassFlowEstimation, self).__init__(
            setup=setup,
            name="Experiment Page 3: Massflow Estimation",
        )
        self.p_gain = AnnotatedSlider(min=0, max=0.3, title="K_p")
        self.i_gain = AnnotatedSlider(min=0, max=0.3, title="K_i")
        self.d_gain = AnnotatedSlider(min=0, max=0.3, title="K_d")
        self.p_gain.slider.valueChanged.connect(self.set_p_value)
        self.i_gain.slider.valueChanged.connect(self.set_i_value)
        self.d_gain.slider.valueChanged.connect(self.set_d_value)

        self.flow = AnnotatedSlider(min=0.2, max=1, title="Massflow")
        self.flow.value = self.setup._current_flow_value
        self.flow.slider.valueChanged.connect(self.set_flow_value)

        self.vertical_layout_controls.addWidget(StatusWidget(setup=self.setup))
        self.vertical_layout_controls.addWidget(self.flow)
        self.vertical_layout_controls.addWidget(self.p_gain)
        self.vertical_layout_controls.addWidget(self.i_gain)
        self.vertical_layout_controls.addWidget(self.d_gain)
        # Placeholder to prevent spreading of widgets across vertical space
        self.vertical_layout_controls.addWidget(QLabel(), 1)

        self.vertical_layout_plots.addWidget(self.plot_widget_factory.delta_t())
        self.vertical_layout_plots.addWidget(self.plot_widget_factory.flow())

    def enter_individual(self):
        self.p_gain.value = self.setup.controller.Kp
        self.i_gain.value = self.setup.controller.Ki
        self.d_gain.value = self.setup.controller.Kd
        self.flow.value = self.setup.get_current_flow_value()
        self.disable_competition_mode()
        self.enable_massflow_setting()

    def leave_individual(self):
        self.enable_competition_mode()
        self.disable_massflow_setting()

    def set_flow_value(self):
        self.setup.set_flow(value=self.flow.value)

    def desired_pwm_output(self):
        return 0

    def set_p_value(self):
        self.setup.set_kp(self.p_gain.value)

    def set_i_value(self):
        self.setup.set_ki(self.i_gain.value)

    def set_d_value(self):
        self.setup.set_kd(self.d_gain.value)
