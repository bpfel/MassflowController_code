#!/bin/bash

# Definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

# Setup script
echo -e "${RED}Updating the distribution...${NC}"
sudo apt-get -y update
sudo apt-get -y dist-upgrade
echo -e "${GREEN}Done!${NC}"


# Install sensirion specific packages
echo -e "${RED}Installing sensirion specific drivers...${NC}"
pip install sensirion-shdlc-driver
pip install sensirion-shdlc-sensorbridge
echo -e "${GREEN}Done!${NC}"

# Install pycharm
echo -e "${RED}Downloading and installing pycharm...${NC}"
wget -nc https://download.jetbrains.com/python/pycharm-community-2019.3.2.tar.gz -P ~/Downloads
sudo tar xfz -k ~/Downloads/pycharm-*.tar.gz -C /opt/
echo -e "${GREEN}Done! Pycharm is now executable as `pycharm`'${NC}"

sudo reboot
