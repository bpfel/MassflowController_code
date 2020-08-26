from serial.tools import list_ports
import platform
import os
import logging

logger = logging.getLogger("root")


class DeviceIdentifier:
    """
    The DeviceIdentifier lists all connected USB devices and tries to identify all devices listed in self.serials.

    :param serials: Dictionary with USB names as keys and USB serials as values.

    .. note:
       If the USB serials are unknown when launching the program first simply supply a dictionary with placeholders.
       DeviceIdentifier supplies information on all available devices upon failing to find one of the devices in
       the serials dictionary.


    .. warning:
       Windows detects USB serials differently than Linux. As experienced in the creating of this software,
       a serial read on a Linux system must be appended with the letter 'A' to be detected on a Windows system.
       To offer platform independence the serials must be given in 'Linux-Form' and are automatically appended
       with the letter 'A' when the program is run on Windows.
    """

    def __init__(self, serials: dict):
        self.serials = serials
        self.serial_ports = {}

    def open(self):
        """
        Detects the current os. For Windows the letter 'A' is appended to the Linux-specific serial of the device.
           For Linux an additional tty-setup script is executed to allow detection of all USB devices.
        :return: Returns True if all devices listed in self.serials could be found.
        """
        # todo: Link to tty_setup.sh
        if platform.system() == "Windows":
            logger.debug("Platform identified as Windows.")
            logger.debug(
                "Appending supplied USB serials with 'A' to make them compatible with Windows."
            )
            for device in self.serials.keys():
                self.serials[device] = "{}A".format(self.serials[device])
        elif platform.system() == "Linux":
            logger.debug("Platform identified as Windows")
            logger.debug(
                "Running '01_SETUP/tty_setup.sh' to allow detection of all devices."
            )
            # Setup tty
            dirname = os.path.dirname(__file__)
            filename = os.path.join(dirname, "../../01_SETUP/tty_setup.sh")
            filename = os.path.normpath(filename)
            os.system(filename)
        else:
            logger.warning("Platform could not be detected!")
        # List comports
        ports = list_ports.comports()
        # Identify all needed devices
        any_not_found = False
        # Iterate over all looked for devices
        for device in self.serials.keys():
            # Iterate over available comports
            found = None
            for port in ports:
                serial = port.serial_number
                found = False
                # Check if the currently searched devices is on the current port
                if serial == self.serials[device]:
                    self.serial_ports.update({device: port.device})
                    logger.debug()
                    found = True
                    break
            # If device is not found on any comport log that
            if not found:
                any_not_found = True
                logger.warning(
                    "Device {} with serial {} not found!".format(
                        device, self.serials[device]
                    )
                )
        # If any device is missing give information on available devices
        if any_not_found:
            logger.warning("Available devices:")
            for port in ports:
                logger.warning(
                    "description: {}, serial: {}".format(
                        port.description, port.serial_number
                    )
                )

        return not any_not_found
