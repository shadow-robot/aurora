#!/usr/bin/env bash

set -e # fail on errors
set -x # echo commands run

script_name=`basename "$0"`
command_usage_message="Command usage: ./${script_name} <playbook name> [--debug-branch <name>]"
command_usage_message="${command_usage_message} [<parameter>=<value>] [<parameter>=<value>] ... [<parameter>=<value>]"
if [[ $# == 1 ]]; then
    echo $command_usage_message
    exit 1
fi

playbook=$1
shift

aurora_home=/tmp/aurora
aurora_tools_branch=master

if [[ $# > 2 ]]; then
    if [[ "$1" = "--debug-branch" ]]; then
        aurora_tools_branch=$2
        shift 2
    fi
fi


echo "================================================================="
echo "|                                                               |"
echo "|                 Shadow Ansible bootstraper                    |"
echo "|                                                               |"
echo "================================================================="
echo ""
echo "possible options: "
echo "  * --debug-branch branch of aurora to use. It is needed for scrip debugging (master by default)"
echo ""
echo "example: ./${script_name} docker-deploy image=shadowrobot/dexterous-hand"
echo ""
echo "playbook     = ${playbook}"
echo "debug-branch = ${aurora_tools_branch}"


echo ""
echo " ---------------------------------"
echo " |   Installing needed packages  |"
echo " ---------------------------------"
echo ""

# Wait for apt-get update lock file to be released
while (sudo fuser /var/lib/apt/lists/lock >/dev/null 2>&1) || (sudo fuser /var/lib/dpkg/lock >/dev/null 2>&1) do
    echo "Waiting for apt-get update file lock..."
    sleep 1
done
sudo apt-get update

# Wait for apt-get install lock file to be released
while sudo fuser /var/lib/dpkg/lock >/dev/null 2>&1; do
    echo "Waiting for apt-get install file lock..."
    sleep 1
done

sudo apt-get install -y python-pip git libyaml-dev python-crypto libssl-dev libffi-dev sshpass
rm -rf $aurora_home

git clone --depth 1 -b $aurora_tools_branch https://github.com/shadow-robot/aurora.git $aurora_home

echo ""
echo " -------------------"
echo " | Running Ansible |"
echo " -------------------"
echo ""

pushd $aurora_home

pip install --user -r ./data/requirements.txt
~/.local/bin/ansible-playbook -vvv --ask-become-pass -i ./inventory/local "./playbooks/${playbook}.yml" --extra-vars "$*"

popd

echo ""
echo " ------------------------------------------------"
echo " |            Operation completed               |"
echo " ------------------------------------------------"
echo ""
