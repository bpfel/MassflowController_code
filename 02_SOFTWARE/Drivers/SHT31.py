from sensirion_shdlc_driver import ShdlcSerialPort, ShdlcConnection
from sensirion_shdlc_sensorbridge import SensorBridgePort, SensorBridgeShdlcDevice

import logging
from SensorBase import SensorBase

TIMEOUT_US = 10e5


class Sht3x(SensorBase):
    def __init__(self, serial_port, device_port='ONE', name="Sht3x"):
        super(Sht3x, self).__init__(name)
        self.port = serial_port
        self.ShdlcPort = None
        self.ShdlcDevice = None

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
            self.connect_sensor(port=self.sensor_bridge_port, supply_voltage=3.3, frequency=400000)
        except Exception as e:
            return e
        return True

    def is_connected(self):
        # todo: implement check whether connected
        pass

    def disconnect(self):
        """Called by SensorBase.close upon deletion of this class.

        """
        self.port.close()

    def connect_sensor(self, port, supply_voltage, frequency):
        """Connection of a sensor attached to the sensirion sensor bridge accroding to
        the quick start guide to sensirion-shdlc-sensorbridge.

        Parameters
        ----------
        port : SensorBridgePort
            Either SensorBridgePort.ONE or .TWO. Refers to one of the two RJ45 ports on
            the sensor bridge module.
        supply_voltage : float
            Desired supply voltage in Volts.
        frequency : int
            I2C frequency
        """
        self.ShdlcDevice.set_i2c_frequency(port=port, frequency=frequency)
        self.ShdlcDevice.set_supply_voltage(port=port, voltage=supply_voltage)
        self.ShdlcDevice.switch_supply_on(port=port)

    def measure(self, port=SensorBridgePort.ONE, address=0x44):
        """Implementation of a single shot measurement according to the SHT3x datasheet.

        A high repeatability measurement with clock stretching enabled is performed.

        Parameters
        ----------
        port : SensorBridgePort
            Either SensorBridgePort.ONE or .TWO. Refers to one of the two RJ45 ports on
            the sensor bridge module.
        address : int
            Either 0x44 or 0x45 if the the ADDR pin is connected to logic high

        Returns
        -------
        dict
            Dictionary containing temperature in degrees Celsius and relative humiditiy
             in percent.

        """
        rx_data = self.ShdlcDevice.transceive_i2c(
            port=port,
            address=address,
            tx_data=[0x2C, 0x06],
            rx_length=6,
            timeout_us=TIMEOUT_US)
        # todo: process received data
        return rx_data


if __name__ == "__main__":
    with Sht3x(serial_port="/dev/ttyUSB2", device_port='ONE') as sht:
        sht.open()
        print(sht.measure())
