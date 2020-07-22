#!/bin/bash

# Definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

# get current script location
full_path=$(realpath $0)
dir_path=$(dirname $full_path)

# Enable tty-support for the sensor bridge
# The file below contains the instructions what do to when an SEK-Sensorbridge is connected
# It triggers the installation of the corresponding driver and assigns a tty-port to the device.
echo -e "${RED}Setting up USB devices...${NC}"
# Use current script location to retrieve local file
sudo cp $dir_path/99-sensorbridge.rules /etc/udev/rules.d
echo -e "${GREEN}Done!${NC}"
sudo /bin/sh -c 'echo 0403 7168 >/sys/bus/usb-serial/drivers/ftdi_sio/new_id'
