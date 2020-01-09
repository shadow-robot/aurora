#!/usr/bin/env bash

set -e # fail on errors
#set -x # echo commands run

script_name="bash <(curl -Ls bit.ly/run-aurora)"

if [ $# < 2 ]; then
    command_usage_message="Command usage: ${script_name} <playbook name> [--debug-branch <name>] [--inventory <name>]"
    command_usage_message="${command_usage_message} [--limit <rules>]"
    command_usage_message="${command_usage_message} [<parameter>=<value>] [<parameter>=<value>] ... [<parameter>=<value>]"
    echo "${command_usage_message}"
    exit 1
fi

aurora_home=/tmp/aurora
playbook=$1
aurora_limit=all
shift

while [ $# > 1 ]
do
key="$1"
case ${key} in
    --debug-branch)
    aurora_tools_branch="$2"
    shift 2
    ;;
    --inventory)
    aurora_inventory="$2"
    shift 2
    ;;
    --limit)
    aurora_limit="$2"
    shift 2
    ;;
    --read-input)
    read_input="$2"
    shift 2
    ;;
    --read-secure)
    read_secure="$2"
    shift 2
    ;;
    *)
    break
    ;;
esac
done

if [[ -z ${aurora_tools_branch} ]];
then
    aurora_tools_branch=master
fi

if [[ -z ${aurora_inventory} ]];
then
    aurora_inventory="local/${playbook}"
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
echo "  * --limit             Run a playbook against one or more members of that group (all by default)"
echo "  * --read-input        Prompt for input(s) required by some playbooks (e.g. docker_username,github_login)"
echo "  * --read-secure       Prompt for password(s) required by some playbooks (e.g. docker_password,git_password)"
echo ""
echo "example: ${script_name} docker_deploy --debug-branch F#SRC-2603_add_ansible_bootstrap --inventory local product=hand_e"
echo ""
echo "playbook     = ${playbook}"
echo "debug-branch = ${aurora_tools_branch}"
echo "inventory    = ${aurora_inventory}"
echo "limit        = ${aurora_limit}"

export ANSIBLE_ROLES_PATH="${aurora_home}/ansible/roles"
export ANSIBLE_CALLBACK_PLUGINS="/home/$USER/.ansible/plugins/callback:/usr/share/ansible/plugins/callback:${aurora_home}/ansible/playbooks/callback_plugins"
export ANSIBLE_STDOUT_CALLBACK="custom_retry_runner"

extra_vars=$*
IFS=',' read -ra inputdata <<< "$read_input"
for i in "${inputdata[@]}"; do
    printf "Data input for $i:"
    read -r input_data
    extra_vars="$extra_vars $i=$input_data"
done
IFS=',' read -ra securedata <<< "$read_secure"
for i in "${securedata[@]}"; do
    printf "\nSecure data input for $i:"
    read -rs secure_data
    extra_vars="$extra_vars $i=$secure_data"
done

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
sudo rm -rf ${aurora_home}

git clone --depth 1 -b ${aurora_tools_branch} https://github.com/shadow-robot/aurora.git $aurora_home

echo ""
echo " -------------------"
echo " | Running Ansible |"
echo " -------------------"
echo ""

pushd $aurora_home

pip3 install --user -r ansible/data/ansible/requirements.txt
ansible_flags="-v --ask-become-pass "

if [[ "${aurora_limit}" != "all" ]]; then
    ansible_flags="${ansible_flags} --limit ${aurora_limit} "
fi
if [[ "${playbook}" = "teleop_deploy" ]]; then
    aurora_inventory="ansible/inventory/teleop/${aurora_inventory}"
fi
if [[ "${playbook}" = "server_and_nuc_deploy" ]]; then
    aurora_inventory="ansible/inventory/server_and_nuc/production"
fi
if [[ "${playbook}" = "server_and_nuc_deploy" || "${playbook}" = "teleop_deploy" ]]; then
    ansible_flags="${ansible_flags} --ask-pass "
    echo ""
    echo " ---------------------------------------------------"
    echo " |             SSH and BECOME passwords:           |"
    echo " | SSH: enter the NUC sudo password                |"
    echo " | BECOME: just press enter (same as SSH password) |"
    echo " ---------------------------------------------------"
    echo ""
else
    aurora_inventory="ansible/inventory/${aurora_inventory}"
    echo ""
    echo " --------------------------------------------"
    echo " |             BECOME password:             |"
    echo " | Enter the sudo password of this computer |"
    echo " --------------------------------------------"
    echo ""
fi

ansible_executable=~/.local/bin/ansible-playbook
if [[ ! -f "${ansible_executable}" ]]; then
    ansible_executable=ansible-playbook
fi

#configure DHCP before running the actual playbook
if [[ "${playbook}" = "server_and_nuc_deploy" ]]; then
    "${ansible_executable}" ${ansible_flags} -i "local" "ansible/playbooks/dhcp.yml" --extra-vars "$extra_vars"
    echo ""
    echo " ----------------------------------------------------------------------"
    echo " |    DHCP network ready! Proceeding with server and nuc playbook      |"
    echo " ----------------------------------------------------------------------"
    echo ""
fi
"${ansible_executable}" ${ansible_flags} -i "${aurora_inventory}" "ansible/playbooks/${playbook}.yml" --extra-vars "$extra_vars"

popd

echo ""
echo " ------------------------------------------------"
echo " |            Operation completed               |"
echo " ------------------------------------------------"
echo ""
