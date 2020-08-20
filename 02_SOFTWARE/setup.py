from Drivers.SHT31 import EKS
from Drivers.SFC5400 import Sfc5400
from Drivers.Shdlc_IO import ShdlcIoModule
from Drivers.DeviceIdentifier import DeviceIdentifier
from Utility.MeasurementBuffer import MeasurementBuffer
from Utility.Timer import RepeatTimer
from simple_pid import PID
import logging
import time
import numpy as np
from enum import Enum

FLOW_LIMIT_FOR_HEATING = 20.0


class Mode(Enum):
    IDLE = 0
    FORCE_PWM = 2
    PID = 3


logger = logging.getLogger("root")


class Setup(object):
    # Standard methods
    def __init__(self, serials, t_sampling_s, interval_s):
        # allocate member variables
        self._serials = serials
        self._t_sampling_s = t_sampling_s
        self.interval_s = interval_s
        self._devices = None
        signals = {
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
        }
        self.measurement_buffer = MeasurementBuffer(
            signals=signals,
            buffer_interval_s=self.interval_s,
            sampling_time_s=self._t_sampling_s,
        )
        # Initialize members
        self._measurement_timer = None
        self._eks = None
        self._sfc = None
        self._heater = None
        self._sdp = None
        self._simulation_mode = False
        self._current_pwm_value = 0
        self._current_mode = "Idle"
        self._setpoint = 6
        self._initial_time = time.time()
        self.controller = PID(
            Kp=0.0, Ki=0.0, Kd=0.0, setpoint=self._setpoint, sample_time=0.3, output_limits=(0, 1)
        )

    def open(self):
        # Find all USB devices and identify them
        self._devices = DeviceIdentifier(serials=self._serials)

        if self._devices.open():
            # Connect all sensors / actuators
            self._eks = EKS(serial_port=self._devices.serial_ports["EKS"])
            self._eks.open()
            self._sfc = Sfc5400(serial_port=self._devices.serial_ports["SFC"])
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
        if self._simulation_mode:
            T_1 = 25 + np.random.rand()
            T_2 = 30 + np.random.rand()
            delta_T = T_2 - T_1
            results = {
                "Temperature 1": T_1,
                "Temperature 2": T_2,
                "Humidity 1": 50 + np.random.rand(),
                "Humidity 2": 30 + np.random.rand(),
                "Flow": 50 + np.random.rand(),
                "Time": time.time(),
                "Temperature Difference": delta_T,
                "PWM": self._current_pwm_value,
                "Flow Estimate": self.calculate_massflow_estimate(
                    delta_t=delta_T, pwm=self._current_pwm_value
                ),
                "Target Delta T": self._setpoint,
                "Controller Output P": 0,
                "Controller Output I": 0,
                "Controller Output D": 0,
                "Controller Output": 0,
            }
            self.measurement_buffer.update(results)
            if self._current_mode is Mode.PID:
                desired_pwm = self.controller(input_=delta_T)
                self._current_pwm_value = desired_pwm
        else:
            logger.info("Measuring once...")
            results_eks = self._eks.measure()
            results_sfc = self._sfc.measure()
            results_timestamp = time.time() - self._initial_time
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
            if self._current_mode is Mode.PID:
                desired_pwm = self.controller(input_=delta_T)
                self._set_pwm(desired_pwm)
                (
                    results["Controller Output P"],
                    results["Controller Output I"],
                    results["Controller Output D"],
                ) = self.controller.components
                results["Controller Output"] = self.controller._last_output
            else:
                (
                    results["Controller Output P"],
                    results["Controller Output I"],
                    results["Controller Output D"],
                    results["Controller Output"],
                ) = (0, 0, 0, 0)
            if results_sfc["Flow"] < FLOW_LIMIT_FOR_HEATING:
                self._set_pwm(0)
            self.measurement_buffer.update(results)

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
            self._measurement_timer.cancel()
            self._measurement_timer = None
            logger.info("Stopped measurement thread.")
        else:
            logger.error("Measurement thread not started yet!")

    def _set_pwm(self, value):
        if self._simulation_mode:
            raise RuntimeError("Heating is not allowed in simulation mode!")
        else:
            value = float(value)
            if not 0.0 <= value <= 1.0:
                raise ValueError("PWM value: {} has to be between 0 and 1".format(value))
            # Safety check: If the flow is smaller than 10.0 slm, heating will not be allowed
            if value != 0 and self.measurement_buffer["Flow"][-1] < FLOW_LIMIT_FOR_HEATING:
                value = 0
            self._current_pwm_value = value
            # convert to heater units:
            value = int(value * 65535.0)
            self._heater.set_pwm(pwm_bit=0, dc=value)

    def wrap_set_pwm(self, value):
        if self._current_mode is not Mode.FORCE_PWM:
            raise RuntimeError(
                "PWM cannot be forced if system is not in FORCE_PWM mode!"
            )
        if self._simulation_mode:
            self._current_pwm_value = float(value)
        else:
            self._set_pwm(value)

    def set_setpoint(self, value):
        value = float(value)
        if value < 0:
            raise RuntimeError("This is a heating setup. Not a fridge, dummy!")
        if value > 20:
            raise RuntimeError("This a test setup. Not an oven, du Löli!")
        self._setpoint = value
        self.controller.setpoint = value

    def set_Kp(self, Kp):
        self.set_pid_parameters(Kp=float(Kp))

    def set_Ki(self, Ki):
        self.set_pid_parameters(Ki=float(Ki))

    def set_Kd(self, Kd):
        self.set_pid_parameters(Kd=float(Kd))

    def set_pid_parameters(self, Kp=None, Ki=None, Kd=None):
        if Kp is None:
            Kp = self.controller.Kp
        if Ki is None:
            Ki = self.controller.Ki
        if Kd is None:
            Kd = self.controller.Kd
        self.controller.tunings = (Kp, Ki, Kd)

    def start_pid_controller(self, setpoint=None):
        self._current_mode = Mode.PID
        if setpoint is not None:
            self._setpoint = setpoint

    def start_direct_power_setting(self):
        self._current_mode = Mode.FORCE_PWM
        if self._simulation_mode:
            pass
        else:
            self._set_pwm(value=0)

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
