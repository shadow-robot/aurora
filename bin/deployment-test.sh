#!/usr/bin/env bash

# Copyright 2024 Shadow Robot Company Ltd.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation version 2 of the License.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

set -e # fail on errors
RED='\033[0;31m'
NC='\033[0m' # No Color
#set -x # echo commands run

pip install speedtest-cli distro
REMOTE_PYTHON_FILE="https://raw.githubusercontent.com/shadow-robot/aurora/refs/heads/F%23SWC-16_customer_deployment_checks/bin/sr_deployment_test.py"
LOCAL_PYTHON_FILE="/tmp/sr_deployment_test.py"
# wget $REMOTE_PYTHON_FILE -O $LOCAL_PYTHON_FILE
# python3 $LOCAL_PYTHON_FILE

wget -qO-  $REMOTE_PYTHON_FILE | python3 -

