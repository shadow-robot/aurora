#!/bin/bash
echo "Deploy MPLABX IDE and MPLABX IPE and Go Through the Installer"
wget -P /home/user/Desktop/ https://s3.eu-west-2.amazonaws.com/com.shadowrobot.eu-west-2.public/public_aurora_files/MPLABX-v5.45-linux-installer.run
sudo chmod +x /home/user/Desktop/MPLABX-v5.45-linux-installer.run
sudo /home/user/Desktop/MPLABX-v5.45-linux-installer.run --mode unattended
echo "MPLABX IDE and MPLABX IPE staging is done. Installer will continue unattended."
