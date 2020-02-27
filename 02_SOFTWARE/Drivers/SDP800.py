from sensirion_shdlc_driver import ShdlcSerialPort, ShdlcConnection
from sensirion_shdlc_sensorbridge import SensorBridgePort, SensorBridgeShdlcDevice

import logging
logger = logging.getLogger(__name__)
from Drivers.SensorBase import SensorBase

TIMEOUT_US = 10e5
DIFFERENTIAL_PRESSURE_MEASUREMENT_NAME = "Differential Pressure"


class Sdp800(SensorBase):
    def __init__(self, serial_port, device_port='TWO', name="Sdp800"):
        super(Sdp800, self).__init__(name)
        self.port = serial_port
        self.ShdlcPort = None
        self.ShdlcDevice = None
        self.i2c_address = 0x25

        if device_port == 'ONE':
            self.sensor_bridge_port = SensorBridgePort.ONE
        elif device_port == 'TWO':
            self.sensor_bridge_port = SensorBridgePort.TWO
        else:
            raise ValueError("Incorrect device_port chosen. Select either 'ONE' or 'TWO'.")

    def connect(self):
        try:
            self.ShdlcPort = ShdlcSerialPort(port=self.port, baudrate=460800)
            self.ShdlcDevice = SensorBridgeShdlcDevice(ShdlcConnection(self.ShdlcPort),
                                                       slave_address=0)
            self.ShdlcDevice.blink_led(port=self.sensor_bridge_port)
            self.connect_sensor(supply_voltage=3.3, frequency=400000)
        except Exception as e:
            logger.error("Could not connect sensor  {} : {}".format(self.name, e))
            return False
        return True

    def connect_sensor(self, supply_voltage, frequency):
        """Connection of a sensor attached to the sensirion sensor bridge according to
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

    def is_connected(self):
        # todo: implement check whether connected
        pass

    def disconnect(self):
        """Called by SensorBase.close upon deletion of this class

        """
        self.ShdlcPort.close()

    def measure(self):
        """Implementation of a triggered measurement according to the SDP8xx datasheet.

        A measurement with temperature compensation set for differential pressure and
        with clock stretching enabled is performed.

        Returns
        -------
        dict
            Dictionary containing

        """
        rx_data = self.ShdlcDevice.transceive_i2c(
            port=self.sensor_bridge_port,
            address=self.i2c_address,
            tx_data=[0x36, 0x2F],
            rx_length=10,
            timeout_us=TIMEOUT_US)
        result_differential_pressure = self._convert_differential_pressure(rx_data[1:3])
        return {
            DIFFERENTIAL_PRESSURE_MEASUREMENT_NAME: result_differential_pressure
        }

    def _convert_differential_pressure(self, data):
        """
        Converts the raw sensor data to the actual measured differential pressure according
        to the data sheet Sensirion_DifferentialPressure_Sensors_SDP800
        Parameters
        ----------
        data : bytearray
            2 bytes, namely number 1 (differential pressure MSB) and 2
            (differential pressure LSB) of the answer delivered by the sensor

        Returns
        -------
        float
            The differential pressured measured by the sensor
        """
        adc_out = data[0] << 8 | data[1]
        return adc_out / 60.0

if __name__ == "__main__":
    import sys
    ch = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    with Sdp800(serial_port='/dev/ttyUSB2', device_port='TWO') as sdp:
        sdp.open()
        print(sdp.measure())
