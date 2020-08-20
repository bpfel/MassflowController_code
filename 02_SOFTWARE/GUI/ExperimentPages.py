from PyQt5.QtWidgets import *
from GUI.LivePlots import PlotWidgetFactory
from GUI.CustomWidgets import AnnotatedSlider


class ExperimentPage(QWidget):
    def __init__(self, setup):
        super(ExperimentPage, self).__init__()
        self.setup = setup
        self.plot_widget_factory = PlotWidgetFactory(setup=setup)
        self.vertical_layout_controls = QVBoxLayout()
        self.vertical_layout_plots = QVBoxLayout()
        self.horizontal_layout = QHBoxLayout()
        self.horizontal_layout.addLayout(self.vertical_layout_controls, 1)
        self.horizontal_layout.addLayout(self.vertical_layout_plots, 3)
        self.setLayout(self.horizontal_layout)


class PWMSetting(ExperimentPage):
    def __init__(self, setup):
        super(PWMSetting, self).__init__(setup=setup)
        # Create controls
        self.pwm = AnnotatedSlider(min=0, max=100, title="Heating Power [%]")
        self.pwm.value = self.setup._current_pwm_value
        self.pwm.slider.valueChanged.connect(self.set_pwm_value)

        # Add widgets to layout
        self.vertical_layout_controls.addWidget(self.pwm)
        # Placeholder to prevent spreading of widgets across vertical space
        self.vertical_layout_controls.addWidget(QLabel(), 1)
        self.vertical_layout_plots.addWidget(self.plot_widget_factory.delta_t())
        self.vertical_layout_plots.addWidget(self.plot_widget_factory.power())

    def set_pwm_value(self):
        self.setup.wrap_set_pwm(value=self.pwm.value)


class PIDSetting(ExperimentPage):
    def __init__(self, setup):
        super(PIDSetting, self).__init__(setup=setup)

        # Create controls
        self.p_gain = AnnotatedSlider(min=0, max=0.1, title="K_p")
        self.i_gain = AnnotatedSlider(min=0, max=0.1, title="K_i")
        self.d_gain = AnnotatedSlider(min=0, max=0.1, title="K_d")
        self.p_gain.value = 0.05
        self.i_gain.value = 0
        self.d_gain.value = 0
        self.p_gain.slider.valueChanged.connect(self.set_p_value)
        self.i_gain.slider.valueChanged.connect(self.set_i_value)
        self.d_gain.slider.valueChanged.connect(self.set_d_value)

        # Add widgets to layout
        self.vertical_layout_controls.addWidget(self.p_gain)
        self.vertical_layout_controls.addWidget(self.i_gain)
        self.vertical_layout_controls.addWidget(self.d_gain)
        # Placeholder to prevent spreading of widgets across vertical space
        self.vertical_layout_controls.addWidget(QLabel(), 1)
        self.vertical_layout_plots.addWidget(self.plot_widget_factory.delta_t())
        self.vertical_layout_plots.addWidget(self.plot_widget_factory.pid())

    def set_p_value(self):
        self.setup.set_Kp(value=self.p_gain.value)

    def set_i_value(self):
        self.setup.set_Ki(value=self.i_gain.value)

    def set_d_value(self):
        self.steup.set_Kd(value=self.d_gain.value)
