from Drivers.SHT31 import Sht3x
from Drivers.SFC5400 import Sfc5400
from Drivers.Shdlc_IO import ShdlcIoModule
from Drivers.DeviceIdentifier import DeviceIdentifier

import logging
import sys
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Setup logging
    ch = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.setLevel(logging.DEBUG)

    # Get the comports
    serials = {
        'SDP': 'FTSTZ7P',
        'EKS': 'EKS231R5DL',
        'SFC': 'FTVQSB5S',
        'Heater': 'AM01ZB7J'
    }
    devices = DeviceIdentifier(serials=serials)

    # Connect sensors
    sht1 = Sht3x(serial_port=devices.serial_ports['EKS'], device_port='ONE')
    sht1.open()
    print(sht1.measure())

    # sht1 = Sht3x(serial_port=devices.serial_ports['EKS'], device_port='TWO')
    # sht1.open()
    # print(sht1.measure())

    sfc = Sfc5400(serial_port=devices.serial_ports['SFC'])
    sfc.open()
    print(sfc.measure())

    heater = ShdlcIoModule(serial_port=devices.serial_ports['Heater'])
    heater.
    # test all methods!
    pass
