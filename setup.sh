#!/bin/bash
# Setup script
sudo apt-get update
sudo apt-get dist-upgrade

# Install sensirion specific packages
pip install sensirion-shdlc-driver
pip install sensirion-shdlc-sensorbridge
# Enable tty-support for the sensor bridge
