from Drivers.SHT31 import EKS
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
    IDLE = 0  # Not started yet
    FORCE_PWM_OFF = 1  # User defines PWM
    FORCE_PWM_ON = 2
    PID_OFF = 3  # PID defines PWM, but is inactive
    PID_ON = 4  # PID defines PWM, is active


class Setup(object):
    def __init__(self, serials: dict, t_sampling_s: float, interval_s: float):
        """
        Upon initialization the setup receives serials of the connected USB devices, the target sampling time
           for measurements and the total buffered interval.
        :param serials: Dictionary of device names and corresponding USB serials.
        :param t_sampling_s: Measurement sampling time in seconds.
        :param interval_s: Total buffered time interval in seconds, which in combination with the sampling time defines
           the number of stored measurements.
        """
        # allocate private member variables
        self._serials = serials
        self._t_sampling_s = t_sampling_s
        self._devices = None
        self._buffering = True
        self._measurement_timer = None
        self._eks = None
        self._sfc = None
        self._heater = None
        self._sdp = None
        self._simulation_mode = False
        self._current_pwm_value = 0
        self._current_mode = Mode.IDLE
        self._setpoint = 6  # Temperature difference setpoint

        # allocate public member variables
        self.interval_s = (
            interval_s  # Time interval over which measurements are buffered
        )
        self.measurement_buffer = self._setup_measurement_buffer()  # Measurement buffer
        self.results = None  # Storage for current measurement frame
        self.controller = PID(
            Kp=0.0,
            Ki=0.0,
            Kd=0.0,
            setpoint=self._setpoint,
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
        Finds and opens all the USB devices previously defined within self.serials by their serial number.
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

    def close(self):
        self.stop_measurement_thread()
        if self._simulation_mode:
            pass
        else:
            self._eks.close()
            self._sfc.close()
            self._heater.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
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
            self.close()

    def measure(self):
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

    def _measure_simulation_mode(self):
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
            "Target Delta T": self._setpoint,
        }
        return results

    def _measure_normal_mode(self):
        logger.info("Measuring once...")
        results_eks = self._eks.measure()
        results_sfc = self._sfc.measure()
        results_timestamp = time.time()
        delta_T = results_eks[1]["Temperature"] - results_eks[0]["Temperature"]
        results = {
            "Temperature 1": results_eks[0]["Temperature"],
            "Temperature 2": results_eks[1]["Temperature"],
            "Humidity 1": results_eks[0]["Humidity"],
            "Humidity 2": results_eks[1]["Humidity"],
            "Flow": results_sfc["Flow"],
            "Time": results_timestamp,
            "Temperature Difference": delta_T,
            "PWM": self._current_pwm_value,
            "Flow Estimate": self.calculate_massflow_estimate(
                delta_t=delta_T, pwm=self._current_pwm_value
            ),
            "Target Delta T": self._setpoint,
        }
        return results

    def start_buffering(self):
        if self._buffering:
            logger.error("Cannot start buffering, already recording to buffer!")
        else:
            self._buffering = True
            self.measurement_buffer.clear()

    def stop_buffering(self):
        if not self._buffering:
            logger.error("Cannot stop buffering, not currenly recording to buffer!")
        else:
            self._buffering = False

    def start_measurement_thread(self):
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

    def stop_measurement_thread(self):
        if self._measurement_timer is not None:
            self.set_pwm(0)
            self.controller.reset()
            self._measurement_timer.cancel()
            self._measurement_timer = None
            logger.info("Stopped measurement thread.")
        else:
            logger.error("Measurement thread not started yet!")

    def set_pwm(self, value):
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

    def set_setpoint(self, value):
        value = float(value)
        if value < 0:
            raise RuntimeError("This is a heating setup. Not a fridge, dummy!")
        if value > 20:
            raise RuntimeError("This a test setup. Not an oven, du Löli!")
        self._setpoint = value
        self.controller.setpoint = value

    def set_Kp(self, kp):
        self.set_pid_parameters(kp=float(kp))

    def set_Ki(self, ki):
        self.set_pid_parameters(ki=float(ki))

    def set_Kd(self, kd):
        self.set_pid_parameters(kd=float(kd))

    def set_pid_parameters(self, kp=None, ki=None, kd=None):
        if kp is None:
            kp = self.controller.Kp
        if ki is None:
            ki = self.controller.Ki
        if kd is None:
            kd = self.controller.Kd
        self.controller.tunings = (kp, ki, kd)

    def start_pid_controller(self, setpoint=None):
        self._current_mode = Mode.PID_OFF
        if setpoint is not None:
            self._setpoint = setpoint

    def start_direct_power_setting(self):
        self._current_mode = Mode.FORCE_PWM_OFF
        self.set_pwm(value=0)

    def enable_output(self, desired_pwm_output=0):
        self.controller.reset()
        if self._current_mode is Mode.PID_OFF:
            self._current_mode = Mode.PID_ON
        elif self._current_mode is Mode.FORCE_PWM_OFF:
            self._current_mode = Mode.FORCE_PWM_ON
            self.set_pwm(desired_pwm_output)

    def disable_output(self):
        if self._current_mode is Mode.PID_ON:
            self._current_mode = Mode.PID_OFF
        elif self._current_mode is Mode.FORCE_PWM_ON:
            self._current_mode = Mode.FORCE_PWM_OFF
        self.set_pwm(0)

    @staticmethod
    def calculate_massflow_estimate(delta_t, pwm):
        c_p = 1006.0  # joule / kilogram / kelvin
        resistance = 11  # ohm
        voltage = 24  # volt
        massflow_SI2SLM = 46432
        if delta_t == 0:
            return 0
        else:
            return massflow_SI2SLM * (pwm * voltage ** 2 / (resistance * c_p * delta_t))
