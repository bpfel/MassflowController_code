from serial.tools import list_ports
import platform
import os
import logging

logger = logging.getLogger("root")


class DeviceIdentifier:
    def __init__(self, serials):
        self.serials = serials
        self.serial_ports = {}

    def open(self):
        # Find current os
        if platform.system() == "Windows":
            for device in self.serials.keys():
                self.serials[device] = "{}A".format(self.serials[device])
        elif platform.system() == "Linux":
            # Setup tty
            dirname = os.path.dirname(__file__)
            filename = os.path.join(dirname, "../../01_SETUP/tty_setup.sh")
            filename = os.path.normpath(filename)
            os.system(filename)
        else:
            print("System unknown")
        # List comports
        ports = list_ports.comports()
        # Identify all needed devices
        any_not_found = False
        # Iterate over all looked for devices
        for device in self.serials.keys():
            # Iterate over available comports
            for port in ports:
                serial = port.serial_number
                found = False
                # Check if the currently searched devices is on the current port
                if serial == self.serials[device]:
                    self.serial_ports.update({device: port.device})
                    found = True
                    break
            # If device is not found on any comport log that
            if not found:
                any_not_found = True
                print(
                    "Device {} with serial {} not found!".format(
                        device, self.serials[device]
                    )
                )
        # If any device is missing give information on available devices
        if any_not_found:
            print("Available devices:")
            for port in ports:
                print(
                    "description: {}, serial: {}".format(
                        port.description, port.serial_number
                    )
                )

        return not any_not_found
