#!/bin/bash
echo "Deploy MPLABX IDE and MPLABX IPE and Go Through the Installer"
sudo apt-get -y install wget
wget https://ww1.microchip.com/downloads/en/DeviceDoc/MPLABX-v5.45-linux-installer.tar
echo "where does it download the file"
pwd
echo "where does it download the file"
tar -xvf MPLABX-v5.45-linux-installer.tar -C .
sudo chmod +x MPLABX-v5.45-linux-installer.sh
sudo ./MPLABX-v5.45-linux-installer.sh
echo "MPLABX IDE and MPLABX IPE staging is done. Installer will continue in a new window."
