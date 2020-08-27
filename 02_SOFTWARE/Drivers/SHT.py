from sensirion_shdlc_driver import ShdlcSerialPort, ShdlcConnection
from sensirion_shdlc_sensorbridge import SensorBridgePort, SensorBridgeShdlcDevice
from sensirion_shdlc_driver.errors import ShdlcTimeoutError
from Drivers.SensorBase import SensorBase
from Drivers.PlatformBase import PlatformBase
import logging

logger = logging.getLogger("root")

TIMEOUT_US = 10e5
TEMPERATURE_MEASUREMENT_NAME = "Temperature"
HUMIDITY_MEASUREMENT_NAME = "Humidity"


class EKS(PlatformBase):
    """
    EKS represents a Sensirion Sensor Bridge (EKS) which is used to communicate to a range of sensor via I2C.

    :type serial_port: str
    :param serial_port: Name of the port to which the EKS is connected.
    """

    def __init__(self, serial_port: str) -> None:
        super(EKS, self).__init__(name="EKS")
        self.port = serial_port
        self.ShdlcPort = None
        self.ShdlcDevice = None
        self.sensors = []

    def connect(self) -> bool:
        """
        Attempts to connect to the EKS.
        :return: True if connected sucessifully, otherwise the encountered exception will be returned.
        """
        try:
            self.ShdlcPort = ShdlcSerialPort(port=self.port, baudrate=460800)
            self.ShdlcDevice = SensorBridgeShdlcDevice(
                ShdlcConnection(self.ShdlcPort), slave_address=0
            )
            self.connect_sensors()
        except Exception as e:
            return e
        return True

    def connect_sensors(self) -> None:
        """
        Attempts to connect sensors at both EKS ports.
        """
        # Scan both ports for sensors
        for i in range(2):
            sensor = SHT(device_port=i, shdlc_device=self.ShdlcDevice)
            sensor.open()
            if sensor.is_connected():
                self.sensors.append(sensor)

    def measure(self) -> list:
        """
        Measures both channels if a sensor is attached
        :return: A list of measured values.
        """
        result = []
        for sensor in self.sensors:
            result.append(sensor.measure())
        return result

    def disconnect(self) -> None:
        """
        Closes all connected sensors.
        """
        for sensor in self.sensors:
            sensor.close()
        self.ShdlcPort.close()

    def is_connected(self) -> bool:
        """
        Tests if the EKS is responsive.
        :return: True if the EKs serial number can be read, False otherwise.
        """
        try:
            self.ShdlcDevice.get_serial_number()
        except (TimeoutError, ShdlcTimeoutError, AttributeError):
            return False
        return True


class SHT(SensorBase):
    """
    SHT represents either a SHT85 or an STH31 of the Sensirion Humidity Temperature (SHT) sensor range, connected via
    the Sensirion Sensor Bridge (EKS).

    :type device_port: SensorBridgePort
    :param device_port: EKS port, either ONE or TWO.
    :type shdlc_device: SensorBridgeShdlcDevice
    :param shdlc_device: Instance of the controlling EKS.
    :type name: str
    :param name: Name of the sensor.
    """

    def __init__(
        self,
        device_port: SensorBridgePort,
        shdlc_device: SensorBridgeShdlcDevice,
        name="SHT",
    ) -> None:
        super(SHT, self).__init__(name)
        self.ShdlcDevice = shdlc_device
        self.i2c_address = 0x44

        # Assign the sensor bridge port for the chosen sensor.
        if device_port == 0:
            self.sensor_bridge_port = SensorBridgePort.ONE
        elif device_port == 1:
            self.sensor_bridge_port = SensorBridgePort.TWO
        else:
            logger.error("Incorrect device_port chosen. Select either 0 or 1.")
            raise ValueError("Incorrect device_port chosen. Select either 0 or 1.")

    def connect(self) -> bool:
        """
        Attempts to connect the sensor and signals success by blinking the corresponding port's LEDs.

        :return: Returns True if connected successifully, False otherwise.
        """
        try:
            self.connect_sensor(supply_voltage=3.3, frequency=400000)
            self.ShdlcDevice.blink_led(port=self.sensor_bridge_port)
        except TimeoutError:
            return False
        return True

    def is_connected(self) -> bool:
        """
        Check if the sensor operates correctly
        :return: True if the status register can be read, False otherwise
        """
        try:
            self.read_status_reg()
        except IOError:
            return False
        return True

    def read_status_reg(self) -> bytearray:
        """
        Reads status register
        :return: Status register value as bytearray.
        """
        with self._lock:
            data = self.ShdlcDevice.transceive_i2c(
                port=self.sensor_bridge_port,
                address=self.i2c_address,
                tx_data=[0xF3, 0x2D],
                rx_length=1,
                timeout_us=TIMEOUT_US,
            )
        return data[0]

    def disconnect(self) -> None:
        """
        Called by SensorBase.close upon deletion of this class. Switches supply off.
        """
        self.ShdlcDevice.switch_supply_off(port=self.sensor_bridge_port)

    def connect_sensor(self, supply_voltage: float, frequency: int) -> None:
        """
        Connection of a sensor attached to the sensirion sensor bridge according to
        the quick start guide to sensirion-shdlc-sensorbridge.

        :type supply_voltage: float
        :param supply_voltage: Desired supply voltage in Volts.
        :type frequency: int
        :param frequency: I2C frequency in Hz
        """
        self.ShdlcDevice.set_i2c_frequency(
            port=self.sensor_bridge_port, frequency=frequency
        )
        self.ShdlcDevice.set_supply_voltage(
            port=self.sensor_bridge_port, voltage=supply_voltage
        )
        self.ShdlcDevice.switch_supply_on(port=self.sensor_bridge_port)

    def measure(self) -> dict:
        """
        Implementats a single shot measurement according to the SHT3x datasheet.
        A high repeatability measurement with clock stretching enabled is performed.

        :return: Dictionary containing temperature in degrees Celsius and relative humiditiy
           in percent.
        """
        rx_data = self.ShdlcDevice.transceive_i2c(
            port=self.sensor_bridge_port,
            address=self.i2c_address,
            tx_data=[0x2C, 0x06],
            rx_length=6,
            timeout_us=TIMEOUT_US,
        )
        result_temperature = self._convert_temperature(rx_data[0:2])
        result_humidity = self._convert_humidity(rx_data[3:5])
        return {
            TEMPERATURE_MEASUREMENT_NAME: result_temperature,
            HUMIDITY_MEASUREMENT_NAME: result_humidity,
        }

    def _convert_humidity(self, data: bytearray) -> float:
        """
        Converts the raw sensor data to the actual measured humidity according to the
           data sheet Sensirion_Humidity_Sensors_SHT3x

        :type data: bytearray
        :param data: 2 bytes, namely number 4 (humidity MSB) and 5 (humidity LSB) of the answer delivered by the sensor.
        :return: The relative humidity measured by the sensor in percent.
        """
        adc_out = data[0] << 8 | data[1]
        return 100.0 * adc_out / 0x10000

    def _convert_temperature(self, data: bytearray) -> float:
        """
        Converts the raw sensor data to the actual measured temperature according to the
           data sheet Sensirion_Humidity_Sensors_SHT3x

        :type data: bytearray
        :param data: 2 bytes, namely number 1 (temperature MSB) and 2 (humidity LSB) of the answer delivered by
           the sensor.
        :return: The temperature measured by the sensor in degrees Celsius.
        """
        adc_out = data[0] << 8 | data[1]
        return -45.0 + 175.0 * adc_out / 0x10000


if __name__ == "__main__":
    from Drivers.DeviceIdentifier import DeviceIdentifier
    from Utility.Logger import setup_custom_logger
    from logging import getLevelName

    logger = setup_custom_logger(name="root", level=getLevelName("DEBUG"))

    serials = {
        "EKS": "EKS231R5DL",
    }
    devices = DeviceIdentifier(serials=serials)
    with EKS(serial_port=devices.serial_ports["EKS"]) as eks:
        eks.open()
        print(eks.measure())
