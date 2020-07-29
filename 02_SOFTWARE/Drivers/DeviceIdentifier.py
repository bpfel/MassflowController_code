from serial.tools import list_ports
import platform
import os
import logging

logger = logging.getLogger('root')


class DeviceIdentifier:
    def __init__(self, serials):
        # Find current os
        if platform.system() == 'Windows':
            print('We re on windows')
            for device in serials.keys():
                serials[device] = '{}A'.format(serials[device])
        elif platform.system() == 'Linux':
            print('We re on linux')
            # Setup tty
            dirname = os.path.dirname(__file__)
            filename = os.path.join(dirname, '../../01_SETUP/tty_setup.sh')
            filename = os.path.normpath(filename)
            os.system(filename)
        else:
            print('System unknown')
        # List comports
        ports = list_ports.comports()
        # Identify all needed devices
        self.serial_ports = {}
        any_not_found = False
        # Iterate over all looked for devices
        for device in serials.keys():
            # Iterate over available comports
            for port in ports:
                serial = port.serial_number
                found = False
                # Check if the currently searched devices is on the current port
                if serial == serials[device]:
                    self.serial_ports.update({device: port.device})
                    found = True
                    break
            # If device is not found on any comport log that
            if not found:
                any_not_found = True
                print('Device {} with serial {} not found!'.format(device, serials[device]))
        # If any device is missing give information on available devices
        if any_not_found:
            print('Available devices:')
            for port in ports:
                print('description: {}, serial: {}'.format(port.description, port.serial_number))
