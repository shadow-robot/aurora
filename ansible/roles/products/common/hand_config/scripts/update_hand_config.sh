#!/usr/bin/env bash
# Used to update hand config.
roscd sr_hand_config
git remote set-url origin https://github.com/shadow-robot/sr_hand_config
git pull  
cd ~