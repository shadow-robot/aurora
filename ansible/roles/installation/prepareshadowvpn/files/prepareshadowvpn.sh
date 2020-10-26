#!/bin/bash
echo "Preparing Environment for ShadowRobot VPN"
sudo add-apt-repository -y ppa:nm-l2tp/network-manager-l2tp
sudo apt-get -y update
sudo apt-get -y install network-manager-l2tp-gnome
sudo service xl2tpd stop
sudo update-rc.d xl2tpd disable
echo "Please Log Out and Log Back in to Continue Shadow Robot VPN Configuration"
