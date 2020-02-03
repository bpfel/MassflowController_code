#!/bin/bash
# Setup script
sudo apt-get update
sudo apt-get dist-upgrade

# Install sensirion specific packages
pip install sensirion-shdlc-driver
pip install sensirion-shdlc-sensorbridge

# Install pycharm

# Enable tty-support for the sensor bridge
# The file below contains the instructions what do to when an SEK-Sensorbridge is connected
# It triggers the installation of the corresponding driver and assigns a tty-port to the device.
cp 99-sensorbridge.rules /etc/udev/rules.d
