from sensirion_shdlc_driver import ShdlcSerialPort, ShdlcConnection
from sensirion_shdlc_sensorbridge import SensorBridgePort, SensorBridgeShdlcDevice
from Drivers.SensorBase import SensorBase
import logging
import time

logger = logging.getLogger("root")

TIMEOUT_US = 10e5
DIFFERENTIAL_PRESSURE_MEASUREMENT_NAME = "Differential Pressure"


class SDP800(SensorBase):
    """
    SDP800 represents a Sensirion Differential Pressure Sensor (SDP) connected via the Sensirion Sensor Bridge (EKS).

    .. warning:
       The SDP800 driver is not working correctly yet! Connection to the sensor works, but the return measurements
       appear to be wrongly interpreted.
    """

    def __init__(self, serial_port, device_port="TWO", name="Sdp800") -> None:
        super(SDP800, self).__init__(name)
        self.port = serial_port
        self.ShdlcPort = None
        self.ShdlcDevice = None
        self.i2c_address = 0x25

        if device_port == "ONE":
            self.sensor_bridge_port = SensorBridgePort.ONE
        elif device_port == "TWO":
            self.sensor_bridge_port = SensorBridgePort.TWO
        else:
            raise ValueError(
                "Incorrect device_port chosen. Select either 'ONE' or 'TWO'."
            )

    def connect(self) -> bool:
        """
        Attempts to connect the Sensor Bridge and subsequently connect the sensor.
        :return: True if connected successifully, False otherwise.
        """
        try:
            self.ShdlcPort = ShdlcSerialPort(port=self.port, baudrate=460800)
            self.ShdlcDevice = SensorBridgeShdlcDevice(
                ShdlcConnection(self.ShdlcPort), slave_address=0
            )
            self.ShdlcDevice.blink_led(port=self.sensor_bridge_port)
            self.connect_sensor(supply_voltage=3.3, frequency=400000)
        except Exception as e:
            logger.error("Could not connect sensor  {} : {}".format(self.name, e))
            return False
        return True

    def connect_sensor(self, supply_voltage: float, frequency: float) -> None:
        """
        Connection of a sensor attached to the sensirion sensor bridge according to the quick start guide to
           sensirion-shdlc-sensorbridge.

        :param supply_voltage: Desired supply voltage in Volts.
        :param frequency: I2C frequency
        """
        self.ShdlcDevice.set_i2c_frequency(
            port=self.sensor_bridge_port, frequency=frequency
        )
        self.ShdlcDevice.set_supply_voltage(
            port=self.sensor_bridge_port, voltage=supply_voltage
        )
        self.ShdlcDevice.switch_supply_on(port=self.sensor_bridge_port)

    def is_connected(self):
        # todo: implement this
        raise NotImplementedError(
            "This device does not yet work correctly. Driver needs work."
        )

    def disconnect(self) -> None:
        """
        Called by SensorBase.close upon deletion of this class
        """
        self.ShdlcPort.close()

    def measure(self):
        """
        Implementation of a triggered measurement according to the SDP8xx datasheet.

        A measurement with temperature compensation set for differential pressure and
           with clock stretching enabled is performed.

        :return: Dictionary containing hitherto unknown measurement results.
        """
        # todo: correct this
        rx_data = self.ShdlcDevice.transceive_i2c(
            port=self.sensor_bridge_port,
            address=self.i2c_address,
            tx_data=[0x36, 0x2F],
            rx_length=10,
            timeout_us=TIMEOUT_US,
        )
        result_differential_pressure = self._convert_differential_pressure(rx_data[0:2])
        return {DIFFERENTIAL_PRESSURE_MEASUREMENT_NAME: result_differential_pressure}

    def _convert_differential_pressure(self, data: bytearray) -> float:
        """
        Converts the raw sensor data to the actual measured differential pressure according
           to the data sheet Sensirion_DifferentialPressure_Sensors_SDP800

        :param data: 2 bytes, namely number 1 (differential pressure MSB) and 2 (differential pressure LSB)
           of the answer delivered by the sensor
        :return: The differential pressured measured by the sensor
        """
        adc_out = data[0] << 8 | data[1]
        return adc_out / 60.0


if __name__ == "__main__":
    import sys
    from Utility.Logger import setup_custom_logger
    from logging import getLevelName

    logger = setup_custom_logger(name="root", level=getLevelName("DEBUG"))

    ch = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    with SDP800(serial_port="/dev/ttyUSB2", device_port="TWO") as sdp:
        sdp.open()
        for i in range(0, 100):
            time.sleep(1)
            print(sdp.measure())
