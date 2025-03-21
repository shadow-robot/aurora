#!/usr/bin/env bash

# Copyright 2022-2024 Shadow Robot Company Ltd.
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

is_repo_public() {
  local user_slash_repo=$1
  ERROR=$(curl -fsS "https://api.github.com/repos/${user_slash_repo}" 2>&1 >/dev/null)
  if [ $? -eq 0 ]; then
    printf '%s\n' "The GitHub repo ${user_slash_repo} exists." >&2
    echo "true"
  else
    if [[ "${ERROR}" == *"error: 403"* ]]; then
      echo "403"
    else
      printf '%s\n' "Error: no GitHub repo ${user_slash_repo} found." >&2
      echo "false"
    fi
  fi
}

confirm() {
	# call with a prompt string or use a default
	read -r -p "${1:-[y/N]} " response
	case "$response" in
		[yY][eE][sS]|[yY])
			echo "y"
			;;
		*)
			echo "n"
			;;
	esac
}

are_all_pr_repos_public(){
    REPO_IS_PRIVATE="true"
    printf '\n%s\n' "Testing if repos specified in pr_branches are all public" >&2
    PR_BRANCHES="$@"
    for i in $PR_BRANCHES; do
      echo "Testing URL: ${i}" >&2
      # Convert github URL to shadow-robot/repo_name
      user_slash_repo=$(echo $i | sed -r 's/.*github\.com\///g' | sed -r s'/\/tree.*//g' | sed -r 's/\/pull.*//g')
      REPO_IS_PUBLIC=$(is_repo_public $user_slash_repo)
      if [[ $REPO_IS_PUBLIC == "false" ]]; then
        REPO_IS_PRIVATE="false"
        break
      elif [[ $REPO_IS_PUBLIC == "403" ]]; then
        REPO_IS_PRIVATE="403"
        break
      fi
    done
    echo $REPO_IS_PRIVATE
}

check_github_next_steps(){
    PUBLIC_REPO_STATUS=$1
    NEXT_STEP=0
    if [[ $PUBLIC_REPO_STATUS == "403" ]]; then
        printf '%s' "WARNING: Rate limit exceeded for github api requests." >&2
        printf '%s\n' " It is not currently possible to confirm whether all the URLs specified in PR_BRANCHES belong to public repos" >&2
        printf '%s\n' "(Rate limits only last for 60 minutes, if you are unsure then please try again later)" >&2
        if [[ $(confirm "Would you like to create a key and authenticate it? y/N") == "y" ]]; then
            NEXT_STEP="generate_key"
        elif [[ $(confirm "Would you like to continue without this check? y/N") == "y" ]] ; then
            NEXT_STEP="skip_check"
        else
            NEXT_STEP="exit"
        fi
    elif [[ $PUBLIC_REPO_STATUS == "true" ]]; then
        NEXT_STEP="all_public"
    else
        NEXT_STEP="generate_key"
    fi
    echo "$NEXT_STEP"
}

github_ssh_public_key_path="${HOME}/.ssh/id_rsa.pub"
github_ssh_private_key_path="${HOME}/.ssh/id_rsa"
SKIP_GIT_SSH_AUTH="false"
if [[ $extra_vars == *"pr_branches="* ]]; then
    PR_BRANCHES="$(echo $extra_vars | sed -r 's/.*pr_branches=//g' | sed -r 's/;.*//g')"
    ARE_ALL_REPOS_PUBLIC=$(are_all_pr_repos_public $PR_BRANCHES)
    NEXT_STEPS=$(check_github_next_steps ${ARE_ALL_REPOS_PUBLIC})
    if [[ $NEXT_STEPS == "exit" ]]; then
        exit 0
    elif [[ $NEXT_STEPS == "skip_check" ]]; then
        echo "Skipping ssh auth and github login"
        formatted_extra_vars="$formatted_extra_vars skip_git_ssh_auth=true"
    elif [[ $NEXT_STEPS == "all_public" ]]; then
        echo "All pr_branch URLs are public, continuing without ssh authentication"
        formatted_extra_vars="$formatted_extra_vars skip_git_ssh_auth=true"
    else
        formatted_extra_vars="$formatted_extra_vars skip_git_ssh_auth=false"
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
    fi
fi


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


export PYTHONNOUSERSITE=1
source $aurora_home/bin/conda_utils.sh
export PYTHONPATH="${miniconda_install_location}/lib/python3.8/site-packages:${miniconda_install_location}/bin"

create_conda_ws

fetch_pip_files
fetch_ansible_files

install_pip_packages


# Fix for WSL - THIS IS NOT SUPPORTED AT ALL - Do not read this, don't look at it, don't try to run it, we don't support it
if grep -q "microsoft" /proc/version  && grep -iq "wsl" /proc/version; then
  pip install pyopenssl --upgrade
  WSL_START_DOCKER_COMMAND='wsl.exe --distribution "${WSL_DISTRO_NAME}" --user root --exec /usr/sbin/service docker start'
  if [[ $(which docker | wc -l) -gt 0 ]]; then
    if service docker status 2>&1 | grep -q "is not running"; then
      ${WSL_START_DOCKER_COMMAND}
    fi
  fi
  if [[ $(cat ~/.bashrc  | grep "${WSL_START_DOCKER_COMMAND}" | wc -l) -eq 0 ]]; then
    echo $WSL_START_DOCKER_COMMAND >> ~/.bashrc
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

ansible_executable="${miniconda_install_location}/bin/ansible-playbook"
if [[ ! -f "${ansible_executable}" ]]; then
    ansible_executable=ansible-playbook
fi
ansible_basic_executable="${miniconda_install_location}/bin/ansible"
if [[ ! -f "${ansible_basic_executable}" ]]; then
    ansible_basic_executable=ansible
fi
ansible_galaxy_executable="${miniconda_install_location}/bin/ansible-galaxy"
if [[ ! -f "${ansible_galaxy_executable}" ]]; then
    ansible_galaxy_executable=ansible-galaxy
fi


# install ansible galaxy docker and aws collections
"${ansible_basic_executable}" --version
install_ansible_collections "${ansible_galaxy_executable}"


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
