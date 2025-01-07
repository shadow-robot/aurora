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


echo
echo "================================================================="
echo "|                                                               |"
echo "|                   Shadow Deployment Test                      |"
echo "|                                                               |"
echo "================================================================="

python3_path=$(which python3 || true)
if [[ $(echo $python3_path | wc -c) -gt 1 ]]; then
  echo "python3 found"
else
  echo "python3 not found"
fi

if grep -q "microsoft" /proc/version  && grep -iq "wsl" /proc/version; then
  echo "Likely running on WSL"
fi

pip install speedtest-cli distro
REMOTE_PYTHON_FILE="https://raw.githubusercontent.com/shadow-robot/aurora/refs/heads/master/bin/sr_deployment_test.py"
LOCAL_PYTHON_FILE="/tmp/sr_deployment_test.py"

wget -qO-  $REMOTE_PYTHON_FILE | python3 -

