#!/usr/bin/env bash

# Copyright 2022 Shadow Robot Company Ltd.
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
#set -x # echo commands run

script_name="bash <(curl -Ls bit.ly/run-aurora)"

command_usage_message="Command usage: ${script_name} <playbook name> [--branch <name>] [--inventory <name>]"
command_usage_message="${command_usage_message} [--limit <rules>]"
command_usage_message="${command_usage_message} [<parameter>=<value>] [<parameter>=<value>] ... [<parameter>=<value>]"

if [[ $# -lt 2 ]]; then
    echo "${command_usage_message}"
    exit 1
fi

aurora_home=/tmp/aurora
conda_ws_name="test_aurora"
miniconda_install_location="/home/$USER/.shadow_miniconda"
miniconda_installer="/tmp/Miniconda3-latest-Linux-x86_64.sh"
miniconda_checksum="634d76df5e489c44ade4085552b97bebc786d49245ed1a830022b0b406de5817"

playbook=$1
# playbook="docker_deploy"
aurora_limit=all
shift

while [[ $# -gt 1 ]]
do
key="$1"
case ${key} in
    --branch)
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

if [[ "${playbook}" = "server_and_nuc_deploy" || "${playbook}" = "teleop_deploy" ]]; then
    if [[ -z ${read_secure} ]]; then
        read_secure="sudo_password"
    else
        read_secure=$read_secure",sudo_password"
    fi
fi

if [[ -z ${aurora_tools_branch} ]];
then
    aurora_tools_branch=master
fi

if [[ -z ${aurora_inventory} ]];
then
    if [[ "${playbook}" = "server_and_nuc_deploy" || "${playbook}" = "teleop_deploy" ]]; then
        aurora_inventory=""
    else
        aurora_inventory="local/${playbook}"
    fi
fi


echo "================================================================="
echo "|                                                               |"
echo "|                 Shadow Ansible bootstraper                    |"
echo "|                                                               |"
echo "================================================================="
echo ""
echo "possible options: "
echo "  * --branch            Branch or tag of aurora to use. Master by default. Can be a release tag, e.g. v1.0.0"
echo "  * --inventory         Inventory of servers to use (local by default)"
echo "  * --limit             Run a playbook against one or more members of that group (all by default)"
echo "  * --read-input        Prompt for input(s) required by some playbooks (e.g. docker_username,github_login)"
echo "  * --read-secure       Prompt for password(s) required by some playbooks (e.g. sudo_password,docker_password,git_password)"
echo ""
echo "example: ${script_name} docker_deploy --branch F#SRC-2603_add_ansible_bootstrap --inventory local product=hand_e"
echo ""
echo "playbook     = ${playbook}"
echo "branch       = ${aurora_tools_branch}"
echo "inventory    = ${aurora_inventory}"
echo "limit        = ${aurora_limit}"

export ANSIBLE_ROLES_PATH="${aurora_home}/ansible/roles"
export ANSIBLE_CALLBACK_PLUGINS="/home/$USER/.ansible/plugins/callback:/usr/share/ansible/plugins/callback:${aurora_home}/ansible/playbooks/callback_plugins"
export ANSIBLE_STDOUT_CALLBACK="custom_retry_runner"

# check for := (ROS style) variable assignments (just = should be used)
extra_vars=$*
# extra_vars='product=hand_e image=public.ecr.aws/shadowrobot/dexterous-hand tag=noetic-v1.0.27 container_name="temp_test_1_conda"'
if [[ $extra_vars == *":="* ]]; then
    echo ""
    echo "All aurora variable assignments should be done with just = not :="
    echo ""
    echo "You entered: $extra_vars"
    echo ""
    echo "Please fix the syntax and try again"
    echo ""
    echo "${command_usage_message}"
    exit 1
fi

# create a copy of extra_vars with values containing spaces surrounded by single quotes
old_IFS=$IFS
IFS=";"
# read extra_vars again inside new IFS
extra_vars=$*
formatted_extra_vars=""
for extra_var in $extra_vars; do
    variable="${extra_var%=*}"
    value="${extra_var#*=}"
    # enclose values containing spaces with single quotes
    if [[ "$value" == *' '* ]]; then
        value="'$value'"
    fi
    if [[ $formatted_extra_vars == "" ]]; then
        formatted_extra_vars="$variable=$value"
    else
        formatted_extra_vars="$formatted_extra_vars $variable=$value"
    fi
done
IFS=${old_IFS}

github_ssh_public_key_path="/home/$USER/.ssh/id_rsa.pub"
github_ssh_private_key_path="/home/$USER/.ssh/id_rsa"
if [[ $extra_vars == *"pr_branches="* ]]; then
    echo " -------------------------------------------------------------------------------------"
    echo "Testing SSH connection to Github with ssh -oStrictHostKeyChecking=no -T git@github.com"
    echo "Using SSH key from $github_ssh_private_key_path"
    ssh_test=$(ssh -oStrictHostKeyChecking=no -T git@github.com 2>&1 &)
    if [[ "$ssh_test" == *"You've successfully authenticated"* ]]; then
        echo " ---------------------------------"
        echo "Github SSH key successfully added!"
        echo " ---------------------------------"
    else
        if [[ -z ${read_input} ]]; then
            read_input="github_email"
        else
            read_input=$read_input",github_email"
        fi
        # Wait for apt-get install lock file to be released
        while sudo fuser /var/lib/dpkg/lock >/dev/null 2>&1; do
            echo "Waiting for apt-get install file lock..."
            sleep 1
        done
        sudo apt-get install -y xclip
    fi
fi

IFS=',' read -ra inputdata <<< "$read_input"
for i in "${inputdata[@]}"; do
    printf "Data input for $i:"
    read -r input_data
    if [[ "${i}" = "github_email" ]]; then
        if [[ ! -f "$github_ssh_public_key_path" ]]; then
            ssh-keygen -t rsa -b 4096 -q -C "$github_email" -N "" -f /home/$USER/.ssh/id_rsa
        fi    
        eval "$(ssh-agent -s)"
        ssh-add $github_ssh_private_key_path
        xclip -sel clip < $github_ssh_public_key_path
        echo " ----------------------------------------------------------------------------------------------------"
        echo "There is an ssh public key in $github_ssh_public_key_path"
        echo "xclip is installed and public ssh key is copied into clipboard"
        echo "Right-click the URL below (don't copy the URL since your clipboard has the ssh key)"
        echo "Select Open Link and follow the steps from number 2 onwards:"
        echo "https://docs.github.com/en/github/authenticating-to-github/adding-a-new-ssh-key-to-your-github-account"
        echo " ----------------------------------------------------------------------------------------------------"
        printf "Confirm if you have added the SSH key to your Github account (y/n):"
        read -r ssh_key_added
        if [[ "$ssh_key_added" == "y" ]]; then
            ssh_test=$(ssh -oStrictHostKeyChecking=no -T git@github.com 2>&1 &)
            if [[ "$ssh_test" == *"You've successfully authenticated"* ]]; then
                echo " ---------------------------------"
                echo "Github SSH key successfully added!"
                echo " ---------------------------------"
            else
                echo " ----------------------------------------------------------------------------------------------------"
                echo "Github SSH authentication failed with message: $ssh_test"
                echo " ----------------------------------------------------------------------------------------------------"
                exit 1
            fi
        else
            echo "You have specified pr_branches but haven't added a Github SSH key"
            echo "Unable to proceed. See the link below"
            echo "https://docs.github.com/en/github/authenticating-to-github/adding-a-new-ssh-key-to-your-github-account"
            exit 1
        fi
    fi
    formatted_extra_vars="$formatted_extra_vars $i=$input_data"
done
IFS=',' read -ra securedata <<< "$read_secure"
for i in "${securedata[@]}"; do
    printf "\nSecure data input for $i:"
    read -rs secure_data
    while [[ "${i}" = "customer_key" && "${#secure_data}" -ne 40 ]]; do
        printf "\nSecure data input for $i is not valid\nIt should be 40 characters long\nYours was: ${#secure_data} characters long\nPlease enter a valid $i\n"
        printf "\nSecure data input for $i:"
        read -rs secure_data
    done
    formatted_extra_vars="$formatted_extra_vars $i=$secure_data"
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
# Pip is broken at the moment and can't find base packages so a reinstall is required.
# curl https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py && python3 /tmp/get-pip.py --force-reinstall && rm /tmp/get-pip.py
sudo apt-get install -y git jq #libyaml-dev libssl-dev libffi-dev sshpass lsb-release
# pip3 install --user -U pip
#sudo chown $USER:$USER $aurora_home || true
sudo rm -rf ${aurora_home}

git clone --depth 1 -b ${aurora_tools_branch} https://github.com/shadow-robot/aurora.git $aurora_home

echo ""
echo " -------------------"
echo " | Running Ansible |"
echo " -------------------"
echo ""

pushd $aurora_home

# ansible_version_pip3=$(pip3 freeze | grep ansible== | tr -d "ansible==")
# if [[ "${ansible_version_pip3}" != "" && "${ansible_version_pip3}" != *"4.2.0"* ]]; then
#     echo "Uninstalling pre-existing pip3 Ansible version $ansible_version_pip3 which is not supported by aurora, if prompted for sudo password, please enter it"
#     pip3 uninstall -y ansible-base ansible-core ansible
#     sudo pip3 uninstall -y ansible-base ansible-core ansible
# fi
# ansible_version_pip2=$(pip2 freeze | grep ansible== | tr -d "ansible==")
# if [[ "${ansible_version_pip2}" != "" && "${ansible_version_pip2}" != *"4.2.0"* ]]; then
#     echo "Uninstalling pre-existing pip2 Ansible version $ansible_version_pip2 which is not supported by aurora, if prompted for sudo password, please enter it"
#     pip2 uninstall -y ansible-base ansible-core ansible
#     sudo pip2 uninstall -y ansible-base ansible-core ansible
# fi

re="^Codename:[[:space:]]+(.*)"
while IFS= read -r line; do
    if [[ $line =~ $re ]]; then
        codename="${BASH_REMATCH[1]}"
    fi
done < <(lsb_release -a 2>/dev/null)

# if [[ $codename == "bionic" ]]; then
#     pip3 install --user -r ansible/data/ansible/bionic/requirements.txt
# else
#     pip3 install --user -r ansible/data/ansible/requirements.txt
# fi

while [[ $(echo $CONDA_PREFIX  | wc -c) -gt 1 ]]; do
  conda deactivate
done

attempts=1
while ! $(echo "${miniconda_checksum} ${miniconda_installer}" | sha256sum --status --check); do
  if [[ -f "$miniconda_installer" ]]; then
    rm $miniconda_installer
  fi
  echo "Attempt number ${attempts}: "
  wget -O $miniconda_installer https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
  attempts=$(( attempts + 1 ))
  if [[ $(echo $attempts) -gt 3 ]]; then
    echo "Maximim attempts to fetch ${miniconda_installer} failed. Has the checksum changed?"
    echo "  Previously known good checksum: ${miniconda_checksum}"
    echo "  Current checksum:               $(sha256sum $miniconda_installer)"
    exit 0
  fi
done

bash /tmp/Miniconda3-latest-Linux-x86_64.sh -u -b -p $miniconda_install_location

if [[ $(echo $PATH  | grep "${miniconda_install_location}/bin" | wc -l) -eq 0 ]]; then
  PATH="${PATH}:${miniconda_install_location}/bin"
fi

${miniconda_install_location}/bin/conda create -y -n ${conda_ws_name} python=3.8 && source ${miniconda_install_location}/bin/activate ${conda_ws_name}
python -m pip install yq
pip_package_downloads_path="/tmp/aurora_host_pip_packages"
mkdir -p $pip_package_downloads_path
remote_packages=$(curl -Ls http://shadowrobot.aurora-host-packages.s3.eu-west-2.amazonaws.com/ | xq | grep pip_packages | grep 'Key' | sed -r 's/.*pip_packages\///g' | sed -r 's/",//g')
# remote_packages=$(curl -Ls http://shadowrobot.aurora-host-packages.s3.eu-west-2.amazonaws.com/ | yq --input-format xml  | grep 'Key:' | sed -r 's/.*pip_packages\///g')
local_only=$(comm -23 <(ls $pip_package_downloads_path | sort) <(for x in $( echo "${remote_packages}"); do echo $x; done | sort))
remote_only=$(comm -13 <(ls $pip_package_downloads_path | sort) <(for x in $( echo "${remote_packages}"); do echo $x; done | sort))

echo "Packages found locally that are not in the bucket: ${local_only}"
echo "Packages found in the bucket that we don't have a local copy of: ${remote_only}"

if [[ $(echo "${local_only}" | wc -c) -gt 1 ]]; then 
  echo "Additional downloaded packages detecting, removing them..."
  for local_package in $(echo ${local_only}); do
    echo "  removing: ${pip_package_downloads_path}/${local_package}"
    rm ${pip_package_downloads_path}/${local_package}
  done
else
  echo "No additional local packages found, continuing..."
fi


if [[ $(echo "${remote_only}" | wc -c) -gt 1 ]]; then
  echo "Remote packages found that we don't have locally, downloading them..."
  for remote_package in $(echo "${remote_only}"); do
    echo "  Downloading: ${remote_package}"
    wget -O ${pip_package_downloads_path}/${remote_package} http://shadowrobot.aurora-host-packages.s3.eu-west-2.amazonaws.com/pip_packages/${remote_package}
  done
fi

python -m pip install ${pip_package_downloads_path}/*

# exit

ansible_flags="-v "

if [[ "${aurora_limit}" != "all" ]]; then
    ansible_flags="${ansible_flags} --limit ${aurora_limit} "
fi
if [[ "${playbook}" = "server_and_nuc_deploy" ]]; then
    if [[ "${aurora_inventory}" = "" ]]; then
        aurora_inventory="ansible/inventory/server_and_nuc/production"
    else
        aurora_inventory="ansible/inventory/server_and_nuc/${aurora_inventory}"
    fi
    ansible_flags="${ansible_flags} --ask-vault-pass"
    echo ""
    echo " ---------------------------------------------------"
    echo " |                 VAULT password:                 |"
    echo " | Enter the VAULT password provided by Shadow     |"
    echo " ---------------------------------------------------"
    echo ""
elif [[ "${playbook}" = "teleop_deploy" ]]; then
    ansible_flags="${ansible_flags} --ask-vault-pass"
    if [[ "${aurora_inventory}" = "" ]]; then
        aurora_inventory="ansible/inventory/teleop/production"
    else
        aurora_inventory="ansible/inventory/teleop/${aurora_inventory}"
    fi

    echo ""
    echo " ---------------------------------------------------"
    echo " |                 VAULT password:                 |"
    echo " | Enter the VAULT password provided by Shadow     |"
    echo " ---------------------------------------------------"
    echo ""
else
    aurora_inventory="ansible/inventory/${aurora_inventory}"
    ansible_flags="${ansible_flags} --ask-become-pass"
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
ansible_basic_executable=~/.local/bin/ansible
if [[ ! -f "${ansible_basic_executable}" ]]; then
    ansible_basic_executable=ansible
fi
ansible_galaxy_executable=~/.local/bin/ansible-galaxy
if [[ ! -f "${ansible_galaxy_executable}" ]]; then
    ansible_galaxy_executable=ansible-galaxy
fi

# install ansible galaxy docker and aws collections
"${ansible_basic_executable}" --version
"${ansible_galaxy_executable}" collection install community.docker amazon.aws

#configure DHCP before running the actual playbook
if [[ "${playbook}" = "server_and_nuc_deploy" ]]; then
# router = false is default group_var, only install dhcp server on laptop if product is not arm+hand and user has not overridden router=true
    if [[ $extra_vars != *"router=true"* && $extra_vars != *"product=arm_"* ]]; then
        "${ansible_executable}" -v -i "ansible/inventory/local/dhcp" "ansible/playbooks/dhcp.yml" --extra-vars "$formatted_extra_vars"
        echo ""
        echo " ----------------------------------------------------------------------"
        echo " |    DHCP network ready! Proceeding with server and nuc playbook      |"
        echo " ----------------------------------------------------------------------"
        echo ""
    fi
fi

"${ansible_executable}" -v ${ansible_flags} -i "${aurora_inventory}" "ansible/playbooks/${playbook}.yml" --extra-vars "$formatted_extra_vars"

popd

echo ""
echo " ------------------------------------------------"
echo " |            Operation completed               |"
echo " ------------------------------------------------"
echo ""
