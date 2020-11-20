from Drivers.SHT import EKS
from Drivers.SFX5400 import SFX5400
from Drivers.Shdlc_IO import ShdlcIoModule
from Drivers.DeviceIdentifier import DeviceIdentifier
from Utility.MeasurementBuffer import MeasurementBuffer
from Utility.Timer import RepeatTimer
from simple_pid import PID
import logging
import time
import numpy as np
from enum import Enum

logger = logging.getLogger("root")

FLOW_LIMIT_FOR_HEATING = 20.0


class Mode(Enum):
    """
    Defines a set of system modes.

    1. IDLE: Before any of the experiment modes has been loaded the system is idle.
    2. FORCE_PWM_OFF: In this mode the pwm can be set directly, but the output is currently turned off.
    3. FORCE_PWM_ON: In this mode the pwm can be set directly.
    4. PID_OFF: In this mode the pid parameters can be set, but the output is currently turned off.
    5. PID_ON: In this mode the pid parameters can be set and the controller is allowed to set pwm values.
    """

    IDLE = 0  # Not started yet
    FORCE_PWM_OFF = 1  # User defines PWM
    FORCE_PWM_ON = 2
    PID_OFF = 3  # PID defines PWM, but is inactive
    PID_ON = 4  # PID defines PWM, is active


class Setup(object):
    """
    The Setup handles all interaction with the hardware of the experiment.

    :type serials: dict
    :param serials: Dictionary of device names and corresponding USB serials.
    :type t_sampling_s: float
    :param t_sampling_s: Measurement sampling time in seconds.
    :type interval_s: float
    :param interval_s: Total buffered time interval in seconds, which in combination with the sampling time defines
       the number of stored measurements.
    """

    def __init__(self, config: dict):
        # allocate private member variables
        self._serials = config['serials']
        self._t_sampling_s = config['t_sampling']
        self._devices = None
        self._buffering = True
        self._measurement_timer = None
        self._eks = None
        self._sfc = None
        self._heater = None
        self._sdp = None
        self._simulation_mode = False
        self._current_pwm_value = 0
        self._current_flow_value = 0
        self._current_mode = Mode.IDLE
        self.temperature_difference_setpoint = config[
            'temperature_difference_set_point']  # Temperature difference setpoint
        self._delta_T = 0  # Static state temperature difference for calibration
        self.config = config

        # allocate public member variables
        self.interval_s = config['interval']
        self.measurement_buffer = self._setup_measurement_buffer()  # Measurement buffer
        self.results = None  # Storage for current measurement frame
        self.controller = PID(
            Kp=0.0,
            Ki=0.0,
            Kd=0.0,
            setpoint=self.temperature_difference_setpoint,
            sample_time=0.3,
            output_limits=(0, 1),
        )

    def _setup_measurement_buffer(self) -> MeasurementBuffer:
        """
        Defines the set of recorded signals and creates a corresponding MeasurementBuffer.

        :return: An instance of MeasurementBuffer containing a deque instance for every signal.
        """
        # todo: Link to MeasurementBuffer class
        signals = [
            "Temperature 1",
            "Temperature 2",
            "Humidity 1",
            "Humidity 2",
            "Flow",
            "Time",
            "Temperature Difference",
            "PWM",
            "Flow Estimate",
            "Target Delta T",
            "Controller Output P",
            "Controller Output I",
            "Controller Output D",
            "Controller Output",
        ]
        return MeasurementBuffer(
            signals=signals,
            buffer_interval_s=self.interval_s,
            sampling_time_s=self._t_sampling_s,
        )

    def open(self) -> None:
        """
        Finds and opens all the USB devices previously defined within `self.serials` by their serial number.
        If one of the devices is not responsive or cannot be found, the setup is switching to simulation mode
        in which all measurements are simulated. This allows to test the GUI without any attached devices.
        """
        # todo: Link to DeviceIdentifier
        self._devices = DeviceIdentifier(serials=self._serials)

        if self._devices.open():
            # Connect all sensors / actuators
            self._eks = EKS(serial_port=self._devices.serial_ports["EKS"])
            self._eks.open()
            self._sfc = SFX5400(serial_port=self._devices.serial_ports["SFC"])
            self._sfc.open()
            self._heater = ShdlcIoModule(
                serial_port=self._devices.serial_ports["Heater"]
            )
            self._heater.open()

            eks_online = self._eks.is_connected()
            sfc_online = self._sfc.is_connected()
            heater_online = self._heater.is_connected()

            if not all([eks_online, sfc_online, heater_online]):
                self._simulation_mode = True
                logger.warning("Entering simulation mode.")
        else:
            self._simulation_mode = True
            logger.warning("Entering simulation mode.")

    def close(self) -> None:
        """
        Closes all connected devices.
        """
        self.stop_measurement_thread()
        if self._simulation_mode:
            pass
        else:
            self._eks.close()
            self._sfc.close()
            self._heater.close()

    def __enter__(self):
        """
        Ensures compatibility with 'with' statement.
        :return: Returns a reference to the current instance.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Called when exiting the context established by the 'with' statement.

        .. warning: Only use this class inside a 'with' statement to ensure calling the shut down procedure for every
           connected platform even upon an unscheduled end of the program.
        """
        if isinstance(exc_val, KeyboardInterrupt):
            logger.info("Experiment aborted with Keyboard-Interrupt!")
            self.close()
            return True
        elif isinstance(exc_val, BaseException) or isinstance(exc_val, Exception):
            logger.info(
                "An unhandled error of type '{}' occured. "
                "Please check console output!".format(exc_type.__name__)
            )
            self.close()
        else:
            logger.info("Experiment ended regularly.")
            self.close()

    def measure(self) -> None:
        """
        Handles measuring and storing signals depending on the system mode and handles updating the PID
        controller output.

        .. seealso::
           :meth:`_measure_simulation_mode`
           :meth:`_measure_normal_mode`
           :mod:`Utility.MeasurementBuffer.MeasurementBuffer`
        """
        # Retrieve all recorded signals depending on system mode
        if self._simulation_mode:
            results = self._measure_simulation_mode()
        else:
            results = self._measure_normal_mode()

        # Calculate control related signals depending on whether the controller is active
        if self._current_mode is Mode.PID_ON:
            desired_pwm = self.controller(input_=results["Temperature Difference"])
            (
                results["Controller Output P"],
                results["Controller Output I"],
                results["Controller Output D"],
            ) = self.controller.components
            results["Controller Output"] = self.controller._last_output
        else:
            desired_pwm = 0
            (
                results["Controller Output P"],
                results["Controller Output I"],
                results["Controller Output D"],
                results["Controller Output"],
            ) = (0, 0, 0, 0)

        # Decide whether to set a new pwm value:
        # If the flow is too low do not heat!
        if results["Flow"] < FLOW_LIMIT_FOR_HEATING:
            self.set_pwm(0)
        # If we're in PID mode set the previously calculated value
        elif self._current_mode is Mode.PID_ON:
            self._current_pwm_value = desired_pwm
            self.set_pwm(desired_pwm)
        # If we're not in PID mode the pwm setting is handled directly via the slider
        else:
            pass

        # Store the current measurement
        self.results = results
        if self._buffering:
            # Buffer multiple measurements in the measurement buffer
            self.measurement_buffer.update(results)

    def _measure_simulation_mode(self) -> dict:
        """
        When no devices are connected random values are generated instead of actual measurements.

        :return: A dictionary with all signals
        """
        T_1 = 25 + np.random.rand()
        T_2 = 30 + np.random.rand()
        delta_T = T_2 - T_1
        results_timestamp = time.time()
        results = {
            "Temperature 1": T_1,
            "Temperature 2": T_2,
            "Humidity 1": 50 + np.random.rand(),
            "Humidity 2": 30 + np.random.rand(),
            "Flow": 50 + np.random.rand(),
            "Time": results_timestamp,
            "Temperature Difference": delta_T,
            "PWM": self._current_pwm_value,
            "Flow Estimate": self.calculate_massflow_estimate(
                delta_t=delta_T, pwm=self._current_pwm_value
            ),
            "Target Delta T": self.temperature_difference_setpoint,
        }
        return results

    def _measure_normal_mode(self) -> dict:
        """
        Measures all devices.

        :return: A dictionary with all measured signals.
        """
        logger.info("Measuring once...")
        results_eks = self._eks.measure()
        results_sfc = self._sfc.measure()
        results_timestamp = time.time()
        delta_T = results_eks[1]["Temperature"] - results_eks[0]["Temperature"] - self._delta_T
        results = {
            "Temperature 1": results_eks[0]["Temperature"],
            "Temperature 2": results_eks[1]["Temperature"] - self._delta_T,
            "Humidity 1": results_eks[0]["Humidity"],
            "Humidity 2": results_eks[1]["Humidity"],
            "Flow": results_sfc["Flow"],
            "Time": results_timestamp,
            "Temperature Difference": delta_T,
            "PWM": self._current_pwm_value,
            "Flow Estimate": self.calculate_massflow_estimate(
                delta_t=delta_T, pwm=self._current_pwm_value
            ),
            "Target Delta T": self.temperature_difference_setpoint,
        }
        return results

    def start_buffering(self) -> None:
        """
        Start recording measurements in the MeasurementBuffer and delete previously recorded measurements.
        """
        if self._buffering:
            logger.error("Cannot start buffering, already recording to buffer!")
        else:
            self._buffering = True
            self.measurement_buffer.clear()

    def stop_buffering(self) -> None:
        """
        Stop recording measurements in the MeasurementBuffer.
        """
        if not self._buffering:
            logger.error("Cannot stop buffering, not currenly recording to buffer!")
        else:
            self._buffering = False

    def start_measurement_thread(self) -> None:
        """
        Creates a thread.Timer that schedules future measurements at the desired sampling time.

        .. seealso::
           :mod:`Utility.Timer.RepeatTimer`
        """
        if self._measurement_timer is None:
            self.measurement_buffer.clear()
            self._measurement_timer = RepeatTimer(
                interval=self._t_sampling_s, function=self.measure
            )
            self._measurement_timer.start()
            logger.info(
                "Started measurement thread running at t_s={} s".format(
                    self._t_sampling_s
                )
            )
        else:
            logger.error("Measurement thread already running!")

    def stop_measurement_thread(self) -> None:
        """
        Cancels the current measurement thread.
        """
        if self._measurement_timer is not None:
            self.set_pwm(0)
            self.controller.reset()
            self._measurement_timer.cancel()
            self._measurement_timer = None
            logger.info("Stopped measurement thread.")
        else:
            logger.error("Measurement thread not started yet!")

    def set_pwm(self, value: float) -> None:
        """
        Safely sets the desired PWM value depending on the current system mode.

        :type value: float
        :param value: Desired PWM value as a normalized value between 0 and 1.

        .. seealso::
           :mod:`setup.Mode`
        """
        if self._simulation_mode:
            self._current_pwm_value = 0
        elif self._current_mode in [Mode.IDLE, Mode.FORCE_PWM_OFF, Mode.PID_OFF]:
            self._heater.set_pwm(pwm_bit=0, dc=0)
            self._current_pwm_value = 0
        elif self._current_mode in [Mode.FORCE_PWM_ON, Mode.PID_ON]:
            value = float(value)
            if not 0.0 <= value <= 1.0:
                raise ValueError(
                    "PWM value: {} has to be between 0 and 1".format(value)
                )
            # Safety check: If the flow is smaller than 20.0 slm, heating will not be allowed
            if value != 0:
                if self.measurement_buffer["Flow"]:
                    if self.measurement_buffer["Flow"][-1] < FLOW_LIMIT_FOR_HEATING:
                        value = 0
                else:
                    value = 0
            # Register the newly set pwm value for later recording
            self._current_pwm_value = value
            # convert to heater units:
            value = int(value * 65535.0)
            self._heater.set_pwm(pwm_bit=0, dc=value)

    def set_setpoint(self, value: float) -> None:
        """
        Allows to define the temperature difference setpoint.

        :type value: float
        :param value: Positive value smaller 20 degrees.
        """
        value = float(value)
        if value < 0:
            raise RuntimeError("This is a heating setup. Not a fridge, dummy!")
        if value > 20:
            raise RuntimeError("This a test setup. Not an oven, du Löli!")
        self.temperature_difference_setpoint = value
        self.controller.setpoint = value

    def set_kp(self, kp: float) -> None:
        """
        Allows setting the Kp gain of the controller.

        :type kp: float
        :param kp: Kp gain of the controller.
        """
        self.set_pid_parameters(kp=float(kp))

    def set_ki(self, ki: float) -> None:
        """
        Allows setting the Ki gain of the controller.

        :type ki: float
        :param ki: Ki gain of the controller
        """
        self.set_pid_parameters(ki=float(ki))

    def set_kd(self, kd: float) -> None:
        """
        Allows setting the Kd gain of the controller.

        :type kd: float
        :param kd: Kd gain of the controller
        """
        self.set_pid_parameters(kd=float(kd))

    def set_pid_parameters(self, kp=None, ki=None, kd=None) -> None:
        """
        Interface to the pid-setting functionality of simple_pid.

        :type kp: float
        :param kp: Kp gain of the controller
        :type ki: float
        :param ki: Ki gain of the controller
        :type kd: float
        :param kd: Kd gain of the controller
        """
        if kp is None:
            kp = self.controller.Kp
        if ki is None:
            ki = self.controller.Ki
        if kd is None:
            kd = self.controller.Kd
        self.controller.tunings = (kp, ki, kd)

    def set_flow(self, value):
        """
        Interface to the SFC5xxx drive for defining the current flow
        setpoint

        :type flow: float
        :param flow: The desired massflow in normalized units, in [0, 1].
        """
        if 0.0 <= value <= 1:
            self._sfc.set_flow(setpoint_normalized=value)

    def start_pid_controller(self, setpoint=None) -> None:
        """
        Start pid mode with the output set to off.

        :type setpoint: float
        :param setpoint: Can be used to define a new temperature difference setpoint.
        """
        self._current_mode = Mode.PID_OFF
        if setpoint is not None:
            self.temperature_difference_setpoint = setpoint

    def start_direct_power_setting(self) -> None:
        """
        Start pwm mode with the output set to off.
        """
        self._current_mode = Mode.FORCE_PWM_OFF
        self.set_pwm(value=0)

    def enable_output(self, desired_pwm_output=0) -> None:
        """
        Enables the output in either pwn or pid mode.

        :type desired_pwm_output: float
        :param desired_pwm_output: Optionally enable pwm mode with a predefined nonzero output.
        """
        self.controller.reset()
        if self._current_mode is Mode.PID_OFF:
            self._current_mode = Mode.PID_ON
        elif self._current_mode is Mode.FORCE_PWM_OFF:
            self._current_mode = Mode.FORCE_PWM_ON
            self.set_pwm(desired_pwm_output)

    def disable_output(self) -> None:
        """
        Disable the output for either pwm or pid mode.
        """
        if self._current_mode is Mode.PID_ON:
            self._current_mode = Mode.PID_OFF
        elif self._current_mode is Mode.FORCE_PWM_ON:
            self._current_mode = Mode.FORCE_PWM_OFF
        self.set_pwm(0)

    def set_temperature_calibration(self) -> None:
        """
        Record the current temperature offset, assuming steady state.
        """
        delta_T = self.results['Temperature Difference']
        threshold = 0.5
        if delta_T > threshold:
            logger.warning("Calibration attempted, delta T: {} larger than threshold: {}".format(delta_T, threshold))
        else:
            self._delta_T = delta_T

    def reset_temperature_calibration(self) -> None:
        """
        Reset the current temperature offset to zero.
        """
        self._delta_T = 0

    def reverse_temp_sensors(self) -> None:
        """
        Reverse the order of the temperature sensors if the have been set up wrongly.
        """
        self._eks.reverse_sensor_order()

    @staticmethod
    def calculate_massflow_estimate(delta_t: float, pwm: float) -> float:
        """
        Calculate the massflow estimate depending on the measured temperature difference and the current output power

        :type delta_t: float
        :param delta_t: Measured temperature difference
        :type pwm: float
        :param pwm: Current output power
        """
        c_p = 1006.0  # joule / kilogram / kelvin
        resistance = 11  # ohm
        voltage = 24  # volt
        massflow_SI2SLM = 46432
        if delta_t == 0:
            return 0
        else:
            return massflow_SI2SLM * (pwm * voltage ** 2 / (resistance * c_p * delta_t))
