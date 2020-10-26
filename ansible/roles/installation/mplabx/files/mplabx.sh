#!/bin/bash
echo "Deploy MPLABX IDE and MPLABX IPE and Go Through the Installer"
sudo apt-get -y install wget
wget https://ww1.microchip.com/downloads/en/DeviceDoc/MPLABX-v5.45-linux-installer.tar
tar -xvf MPLABX-v5.45-linux-installer.tar -C .
sudo chmod +x MPLABX-v5.45-linux-installer.sh
sudo ./MPLABX-v5.45-linux-installer.sh
echo "MPLABX IDE and MPLABX IPE staging is done. Installer will continue in a new window."
