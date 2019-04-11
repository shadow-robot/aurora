#!/usr/bin/env bash

set -e # fail on errors
#set -x # echo commands run

script_name=run-ansible.sh
command_usage_message="Command usage: ./${script_name} <playbook name> [--debug-branch <name>] [--inventory <name>]"
command_usage_message="${command_usage_message} [<parameter>=<value>] [<parameter>=<value>] ... [<parameter>=<value>]"

if [[ $# < 2 ]]; then
    echo $command_usage_message
    exit 1
fi

aurora_home=/tmp/aurora
playbook=$1
shift

while [[ $# > 1 ]]
do
key="$1"
case $key in
    --debug-branch)
    aurora_tools_branch="$2"
    shift
    ;;
    --inventory)
    aurora_inventory="$2"
    shift
    ;;
    *)
    ;;
esac
shift
done

if [ -z "${aurora_tools_branch}" ];
then
    aurora_tools_branch=master
fi

if [ -z "${aurora_inventory}" ];
then
    aurora_inventory=local
fi


echo "================================================================="
echo "|                                                               |"
echo "|                 Shadow Ansible bootstraper                    |"
echo "|                                                               |"
echo "================================================================="
echo ""
echo "possible options: "
echo "  * --debug-branch      Branch of aurora to use. It is needed for scrip debugging (master by default)"
echo "  * --inventory         Inventory of servers to use (local by default)"
echo ""
echo "example: ./${script_name} docker-deploy --debug-branch F#SRC-2603_add_ansible_bootstrap --inventory local product=hand_e"
echo ""
echo "playbook     = ${playbook}"
echo "debug-branch = ${aurora_tools_branch}"
echo "inventory    = ${aurora_inventory}"

export ANSIBLE_ROLES_PATH="${aurora_home}/ansible/roles"

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

sudo apt-get install -y python3-pip git libyaml-dev python-crypto libssl-dev libffi-dev sshpass
sudo chown $USER:$USER $aurora_home || true
sudo rm -rf $aurora_home

git clone --depth 1 -b $aurora_tools_branch https://github.com/shadow-robot/aurora.git $aurora_home

echo ""
echo " -------------------"
echo " | Running Ansible |"
echo " -------------------"
echo ""

pushd $aurora_home

pip3 install --user -r ansible/data/requirements.txt
if [[ "${playbook}" = "teleop-deploy" ]]; then
    ~/.local/bin/ansible-playbook -v --ask-pass --ask-become-pass -i "ansible/inventory/teleop/${aurora_inventory}" "ansible/playbooks/${playbook}.yml" --extra-vars "$*"
else
    echo "normal"
    ~/.local/bin/ansible-playbook -v --ask-become-pass -i "ansible/inventory/${aurora_inventory}" "ansible/playbooks/${playbook}.yml" --extra-vars "$*"
fi

popd

echo ""
echo " ------------------------------------------------"
echo " |            Operation completed               |"
echo " ------------------------------------------------"
echo ""
