#!/bin/bash
echo "Installing Snap BpyTOP package and grant access to it to be able to monitor the system resources, etc."
sudo snap install bpytop
sudo snap connect bpytop:mount-observe
sudo snap connect bpytop:network-control
sudo snap connect bpytop:hardware-observe
sudo snap connect bpytop:system-observe
sudo snap connect bpytop:process-control
sudo snap connect bpytop:physical-memory-observe
echo "BpyTOP package has been installed"
