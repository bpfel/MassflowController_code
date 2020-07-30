from struct import pack
import logging

log = logging.getLogger('root')


class I2cDevice(object):
    def __init__(self, connection, slave_address):
        super(I2cDevice, self).__init__()
        self._connection = connection
        self._slave_address = slave_address
        self._last_command = None

    @property
    def connection(self):
        return self._connection

    @property
    def slave_address(self):
        return self._slave_address

    def execute(self, command, asynchronous=False):
        self._last_command = command
        if asynchronous:
            self._connection.write(self._slave_address, command)
        else:
            return self._connection.execute(self._slave_address, command)

    def read(self):
        return self._connection(self._slave_address, self._last_command)


class I2cConnection(object):
    def __init__(self, transceiver):
        super(I2cConnection, self).__init__()
        self._transceiver = transceiver

    def write(self, slave_address, command):
        return self._interpret_response(command, self._transceive(
            slave_address=slave_address,
            tx_data=command.tx_data,
            rx_length=None,
            read_delay=0,
            timeout=command.timeout
        ))
