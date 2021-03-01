from serial.tools import list_ports
target_serial_number = "FT4NSYW9A"

ports = list_ports.comports()

comport_name = None
for port in ports:
    print('description: {}, serial: {}'.format(port.description, port.serial_number))
    if port.serial_number == target_serial_number:
        comport_name = port.description

print("The comport with the differential pressure sensor is: {}".format(comport_name))


