#!/bin/bash

# Definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

# Setup script
echo -e "${RED}Updating the distribution...${NC}"
sudo apt-get update
sudo apt-get dist-upgrade
echo -e "${GREEN}Done!${NC}"


# Install sensirion specific packages
echo -e "${RED}Installing sensirion specific drivers...${NC}"
pip install sensirion-shdlc-driver
pip install sensirion-shdlc-sensorbridge
echo -e "${GREEN}Done!${NC}"

# Install pycharm
echo -e "${RED}Downloading and installing pycharm...${NC}"
wget -nc https://download.jetbrains.com/python/pycharm-community-2019.3.2.tar.gz -P ~/Downloads
sudo tar xfz ~/Downloads/pycharm-*.tar.gz -C /opt/
sudo /bin/bash -c 'echo export PATH=$PATH:/opt/pycharm*/bin'
sudo cp /opt/pycharm*/bin/pycharm.sh /opt/pycharm*/bin/pycharm
echo -e "${GREEN}Done! Pycharm is now executable as `pycharm`'${NC}"

# Enable tty-support for the sensor bridge
# The file below contains the instructions what do to when an SEK-Sensorbridge is connected
# It triggers the installation of the corresponding driver and assigns a tty-port to the device.
echo -e "${RED}Setting up USB devices...${NC}"
sudo cp 99-sensorbridge.rules /etc/udev/rules.d
echo -e "${GREEN}Done!${NC}"
sudo /bin/sh -c 'echo 0403 7168 >/sys/bus/usb-serial/drivers/ftdi_sio/new_id'
