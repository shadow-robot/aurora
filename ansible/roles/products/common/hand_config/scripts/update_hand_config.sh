#!/usr/bin/env bash
# Used to update hand config.
source /home/user/projects/shadow_robot/base/devel/setup.bash
roscd sr_hand_config & cd ..
git remote set-url origin https://github.com/shadow-robot/sr_hand_config
git pull  
cd ~