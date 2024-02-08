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
RED='\033[0;31m'
NC='\033[0m' # No Color
#set -x # echo commands run

script_name="bash <(curl -Ls bit.ly/run-aurora)"

command_usage_message="Command usage: ${script_name} <playbook name> [--branch <name>] [--inventory <name>]"
command_usage_message="${command_usage_message} [--limit <rules>]"
command_usage_message="${command_usage_message} [<parameter>=<value>] [<parameter>=<value>] ... [<parameter>=<value>]"

if [[ $# -lt 2 ]]; then
    echo "${command_usage_message}"
    exit 1
fi

# Some molecule tests install to `/home/...` (no user account)
if [ -z $USER ]; then
  if [ -z $MY_USERNAME ]; then
    HOME='/home'
  fi
fi

aurora_home=/tmp/aurora
conda_ws_name="aurora_conda_ws"
miniconda_install_root="${HOME}/.shadow_miniconda"
miniconda_install_location="${miniconda_install_root}/miniconda"
miniconda_installer="${miniconda_install_root}/miniconda_installer.sh"
miniconda_installer_url="https://repo.anaconda.com/miniconda/Miniconda3-py311_23.5.2-0-Linux-x86_64.sh"
miniconda_checksum="634d76df5e489c44ade4085552b97bebc786d49245ed1a830022b0b406de5817"
packages_download_root="${miniconda_install_root}/aurora_host_packages"

playbook=$1
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
export ANSIBLE_CALLBACK_PLUGINS="${HOME}/.ansible/plugins/callback:/usr/share/ansible/plugins/callback:${aurora_home}/ansible/playbooks/callback_plugins"
export ANSIBLE_STDOUT_CALLBACK="custom_retry_runner"

# check for := (ROS style) variable assignments (just = should be used)
extra_vars=$*
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

github_ssh_public_key_path="${HOME}/.ssh/id_rsa.pub"
github_ssh_private_key_path="${HOME}/.ssh/id_rsa"
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
            ssh-keygen -t rsa -b 4096 -q -C "$github_email" -N "" -f ${HOME}/.ssh/id_rsa
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

# jq is needed for yq, which installs xq, which helps parse aws s3 http requests
sudo apt-get install -y git jq curl lsb-release libyaml-dev libssl-dev libffi-dev sshpass
sudo chown $USER:$USER $aurora_home || true
sudo rm -rf ${aurora_home}

git clone --depth 1 -b ${aurora_tools_branch} https://github.com/shadow-robot/aurora.git $aurora_home

echo ""
echo " -------------------"
echo " | Running Ansible |"
echo " -------------------"
echo ""

pushd $aurora_home


re="^Codename:[[:space:]]+(.*)"
while IFS= read -r line; do
    if [[ $line =~ $re ]]; then
        codename="${BASH_REMATCH[1]}"
    fi
done < <(lsb_release -a 2>/dev/null)

# We use this variable to figure out which pip packages to download. Packages for focal work on jammy, but bionic needs its own packages
if [[ $codename == *"jammy"* ]]; then
  codename="focal"
fi

mkdir -p $miniconda_install_root
attempts=1
while ! $(echo "${miniconda_checksum} ${miniconda_installer}" | sha256sum --status --check); do
  if [[ -f "$miniconda_installer" ]]; then
    rm $miniconda_installer
  fi
  echo "Attempt number ${attempts}: "
  wget -O $miniconda_installer $miniconda_installer_url
  attempts=$(( attempts + 1 ))
  if [[ $(echo $attempts) -gt 3 ]]; then
    echo "Maximim attempts to fetch ${miniconda_installer} failed. Has the checksum changed?"
    echo "  Previously known good checksum: ${miniconda_checksum}"
    echo "  Current checksum:               $(sha256sum $miniconda_installer)"
    exit 0
  fi
done

bash $miniconda_installer -u -b -p $miniconda_install_location

if [[ $(echo $PATH  | grep "${miniconda_install_location}/bin" | wc -l) -eq 0 ]]; then
  PATH="${PATH}:${miniconda_install_location}/bin"
fi

${miniconda_install_location}/bin/conda create -y -n ${conda_ws_name} python=3.8 && source ${miniconda_install_location}/bin/activate ${conda_ws_name}
python -m pip install yq xq
fetch_new_files() {
  aws_bucket_url=$1
  aws_bucket_dir=$2
  local_download_dir="${packages_download_root}/${aws_bucket_dir}"

  echo "Fetching ${aws_bucket_dir}..."
  mkdir -p $local_download_dir

  remote_packages=$(curl -Ls ${aws_bucket_url} | xq | grep $aws_bucket_dir | grep 'Key' | sed -r "s/.*${aws_bucket_dir}\///g" | sed -r 's/",//g' | sed -r 's;</Key>;;g')

  echo "remote_packages: ${remote_packages}"

  local_only=$(comm -23 <(ls $local_download_dir | sort) <(for x in $( echo "${remote_packages}"); do echo $x; done | sort))
  remote_only=$(comm -13 <(ls $local_download_dir | sort) <(for x in $( echo "${remote_packages}"); do echo $x; done | sort))

  echo "Packages found locally that are not in the bucket: ${local_only}"
  echo "Packages found in the bucket that we don't have a local copy of: ${remote_only}"

  if [[ $(echo "${local_only}" | wc -c) -gt 1 ]]; then
    echo "Additional downloaded packages detecting, removing them..."
    for local_package in $(echo ${local_only}); do
      echo "  removing: ${local_download_dir}/${local_package}"
      rm ${local_download_dir}/${local_package}
    done
  else
    echo "No additional local packages found, continuing..."
  fi

  if [[ $(echo "${remote_only}" | wc -c) -gt 1 ]]; then
    echo "Remote packages found that we don't have locally, downloading them..."
    for remote_package in $(echo "${remote_only}"); do
      echo "  Downloading: ${remote_package}"
      wget -q --show-progress -O ${local_download_dir}/${remote_package} ${aws_bucket_url}/${aws_bucket_dir}/${remote_package}
      if [[ $(stat --print="%s" ${local_download_dir}/${remote_package}) -eq 0 ]]; then
        echo -e "\n${RED}WARNING! The package ${remote_package} from ${aws_bucket_url}/${aws_bucket_dir}/${remote_package} has downloaded a file of zero bytes! This probably means s3 bucket permissions are wrong and is very likely to cause deployment issues on your system. Please contact shadow directly to get this fixed.${NC}\n"
        rm ${local_download_dir}/${remote_package}
      fi
    done
  fi
}

fetch_new_files "http://shadowrobot.aurora-host-packages-${codename}.s3.eu-west-2.amazonaws.com" "pip_packages"
fetch_new_files "http://shadowrobot.aurora-host-packages-${codename}.s3.eu-west-2.amazonaws.com" "ansible_collections"
ANSIBLE_SKIP_CONFLICT_CHECK=1 python -m pip install ${packages_download_root}/pip_packages/*

# Fix for WSL - THIS IS NOT SUPPORTED AT ALL!!!
if grep -q "microsoft" /proc/version  && grep -iq "wsl" /proc/version; then
  # python3 -m pip install pip --upgrade
  pip install pyopenssl --upgrade
  if [[ $(which docker | wc -l) -gt 0 ]]; then
    if service docker status 2>&1 | grep -q "is not running"; then
      wsl.exe --distribution "${WSL_DISTRO_NAME}" --user root --exec /usr/sbin/service docker start
    fi
  fi
fi


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
"${ansible_galaxy_executable}" collection install $(realpath ${packages_download_root}/ansible_collections/*)

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
