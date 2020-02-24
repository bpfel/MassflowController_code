from sensirion_shdlc_driver import ShdlcSerialPort, ShdlcConnection
from sensirion_shdlc_sensorbridge import SensorBridgePort, SensorBridgeShdlcDevice

import logging
from SensorBase import SensorBase

TIMEOUT_US = 10e5
TEMPERATURE_MEASUREMENT_NAME = "Temperature"
HUMIDITY_MEASUREMENT_NAME = "Humidity"


class Sht3x(SensorBase):
    def __init__(self, serial_port, device_port='ONE', name="Sht3x"):
        super(Sht3x, self).__init__(name)
        self.port = serial_port
        self.ShdlcPort = None
        self.ShdlcDevice = None
        self.i2c_address = 0x44

        # Assign the sensor bridge port for the chosen sensor.
        if device_port == 'ONE':
            self.sensor_bridge_port = SensorBridgePort.ONE
        elif device_port == 'TWO':
            self.sensor_bridge_port = SensorBridgePort.TWO
        else:
            raise ValueError("Incorrect device_port chosen. Select either 'ONE' or 'TWO'.")

    def connect(self):
        """Called by SensorBase.__init__(), handles the connection of all sensors

        """
        try:
            self.ShdlcPort = ShdlcSerialPort(port=self.port, baudrate=460800)
            self.ShdlcDevice = SensorBridgeShdlcDevice(ShdlcConnection(self.ShdlcPort), slave_address=0)
            self.ShdlcDevice.blink_led(port=self.sensor_bridge_port)
            self.connect_sensor(supply_voltage=3.3, frequency=400000)
        except Exception as e:
            return e
        return True

    def is_connected(self):
        # todo: implement check whether connected
        pass

    def probe(self):
        """
        Check if the sensor operates correctly
        Returns
        -------
        bool
            True if everything is fine
        """
        try:
            self.read_status_reg()
            return True
        except IOError:
            return False

    def read_status_reg(self):
        """
        Read status register
        Returns
        -------
        bytearray
            status register value
        """
        with self._lock:
            data = self.ShdlcDevice.transceive_i2c(
                port=self.sensor_bridge_port,
                address=self.i2c_address,
                tx_data=[0xF3, 0x2D],
                rx_length=1,
                timeout_us=TIMEOUT_US
            )
        return data[0]

    def disconnect(self):
        """Called by SensorBase.close upon deletion of this class.

        """
        self.port.close()

    def connect_sensor(self, supply_voltage, frequency):
        """Connection of a sensor attached to the sensirion sensor bridge accroding to
        the quick start guide to sensirion-shdlc-sensorbridge.

        Parameters
        ----------
        supply_voltage : float
            Desired supply voltage in Volts.
        frequency : int
            I2C frequency
        """
        self.ShdlcDevice.set_i2c_frequency(port=self.sensor_bridge_port, frequency=frequency)
        self.ShdlcDevice.set_supply_voltage(port=self.sensor_bridge_port, voltage=supply_voltage)
        self.ShdlcDevice.switch_supply_on(port=self.sensor_bridge_port)

    def measure(self):
        """Implementation of a single shot measurement according to the SHT3x datasheet.

        A high repeatability measurement with clock stretching enabled is performed.

        Parameters
        ----------
        Returns
        -------
        dict
            Dictionary containing temperature in degrees Celsius and relative humiditiy
             in percent.

        """
        rx_data = self.ShdlcDevice.transceive_i2c(
            port=self.sensor_bridge_port,
            address=self.i2c_address,
            tx_data=[0x2C, 0x06],
            rx_length=6,
            timeout_us=TIMEOUT_US)
        result_temperature = self._convert_temperature(rx_data[0:2])
        result_humidity = self._convert_humidity(rx_data[3:5])
        return {
            TEMPERATURE_MEASUREMENT_NAME : result_temperature,
            HUMIDITY_MEASUREMENT_NAME : result_humidity
        }

    def _convert_humidity(self, data):
        """
        Converts the raw sensor data to the actual measured humidity according to the
        data sheet Sensirion_Humidity_Sensors_SHT3x
        Parameters
        ----------
        data : bytearray
            2 bytes, namely number 4 (humidity MSB) and 5 (humidity LSB)
            of the answer delivered by the sensor

        Returns
        -------
        float
            The relative humidity measured by the sensor
        """
        adc_out = data[0] << 8 | data[1]
        return 100.0 * adc_out / 0x10000

    def _convert_temperature(self, data):
        """
        Converts the raw sensor data to the actual measured temperature according to the
        data sheet Sensirion_Humidity_Sensors_SHT3x
        Parameters
        ----------
        data : bytearray
            2 bytes, namely number 1 (temperature MSB) and 2 (humidity LSB)
            of the answer delivered by the sensor

        Returns
        -------
        float
            The temperature measured by the sensor

        """
        adc_out = data[0] << 8 | data[1]
        return -45.0 + 175.0 * adc_out / 0x10000

if __name__ == "__main__":
    with Sht3x(serial_port="/dev/ttyUSB2", device_port='ONE') as sht:
        sht.open()
        print(sht.measure())
