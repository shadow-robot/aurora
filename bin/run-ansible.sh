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

AURORA_HOME=/tmp/aurora
SCRIPT_NAME="bash <(curl -Ls bit.ly/run-aurora)"
AURORA_LIMIT=all
PLAYBOOK=""

# Define color escape codes
RED='\e[0;31m'
RESET='\e[0m'
YELLOW='\e[1;33m'
GREEN='\e[0;32m'

print_red() {
    echo -e "${RED}$1${RESET}"
}

print_green() {
    echo -e "${GREEN}$1${RESET}"
}

print_yellow() {
    echo -e "${YELLOW}$1${RESET}"
}

# Set the verbosity level ansible supports up to "vvvvvvvvv" each adding verbosity
VERBOSITY="v"

# Check for debug flag
for arg in "$@"; do
    if [[ "$arg" == "--debug" ]]; then
        print_red "Debug mode enabled"
        set -x # echo commands run
        break
    fi
done

print_startup_message() {
    print_yellow "================================================================="
    print_yellow "|                                                               |"
    print_yellow "|                 Shadow Ansible Deployment Tool                |"
    print_yellow "|                                                               |"
    print_yellow "================================================================="
    print_yellow ""
    print_yellow "possible options: "
    print_yellow "  * --branch            Branch or tag of aurora to use. Master by default. Can be a release tag, e.g. v1.0.0"
    print_yellow "  * --inventory         Inventory of servers to use (local by default)"
    print_yellow "  * --limit             Run a playbook against one or more members of that group (all by default)"
    print_yellow "  * --read-input        Prompt for input(s) required by some playbooks (e.g. docker_username,github_login)"
    print_yellow "  * --read-secure       Prompt for password(s) required by some playbooks (e.g. sudo_password,docker_password,git_password)"
    print_yellow "  * --debug             Run aurora in debug mode printing every command run (very loud)"
    print_yellow ""
    print_yellow "example: ${script_name} docker_deploy --branch F#SRC-2603_add_ansible_bootstrap --inventory local product=hand_e"
    print_yellow ""
    print_yellow "playbook     = ${playbook}"
    print_yellow "branch       = ${aurora_tools_branch}"
    print_yellow "inventory    = ${aurora_inventory}"
    print_yellow "limit        = ${aurora_limit}"
    print_yellow "read-input   = ${read_input}"
    print_yellow "read-secure  = ${read_secure}"
    print_yellow ""
}

# Print the correct usage of the script
command_usage() {
    command_usage_message="Command usage: ${SCRIPT_NAME} <playbook name> [--branch <name>] [--inventory <name>] [--limit <rules>] [<parameter>=<value>] [<parameter>=<value>] ... [<parameter>=<value>]"
    print_red "${command_usage_message}"
}

# Check for the min number of input parameters
check_invalid_input() {
    if [[ $# -lt 2 ]]; then
        command_usage
        exit 1
    fi

    # Some molecule tests install to `/home/...` (no user account)
    if [ -z "$USER" ]; then
        if [ -z "$MY_USERNAME" ]; then
            HOME='/home'
        fi
    fi
}

# Check if the playbook exists then set the variables
set_variables() {
    PLAYBOOK=$1
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
                AURORA_LIMIT="$2"
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

    if [[ "${PLAYBOOK}" = "server_and_nuc_deploy" || "${PLAYBOOK}" = "teleop_deploy" ]]; then
        if [[ -z ${read_secure} ]]; then
            read_secure="sudo_password"
        else
            read_secure=$read_secure",sudo_password"
        fi
    fi

    if [[ -z ${aurora_tools_branch} ]]; then
        aurora_tools_branch=master
    fi

    if [[ -z ${aurora_inventory} ]]; then
        if [[ "${PLAYBOOK}" = "server_and_nuc_deploy" || "${PLAYBOOK}" = "teleop_deploy" ]]; then
            aurora_inventory=""
        else
            aurora_inventory="local/${PLAYBOOK}"
        fi
    fi
}

# Check for := (ROS style) variable assignments (just = should be used)
check_variable_syntax() {
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
}

# Create a copy of extra_vars with values containing spaces surrounded by single quotes
format_extra_vars() {
    old_IFS=$IFS
    IFS=";"
    extra_vars=$*
    formatted_extra_vars=""
    for extra_var in $extra_vars; do
        variable="${extra_var%=*}"
        value="${extra_var#*=}"
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
}


is_repo_public() {
    local user_slash_repo=$1
    ERROR=$(curl -fsS "https://api.github.com/repos/${user_slash_repo}" 2>/dev/null)
    if [ $? -eq 0 ]; then
        printf '%s\n' "The GitHub repo ${user_slash_repo} exists." >&2
        echo "true"
    else
        if [[ "${ERROR}" == *"error: 403"* ]]; then
            print_red "403"
        else
            printf '%s\n' "Error: no GitHub repo ${user_slash_repo} found." >&2
            echo "false"
        fi
    fi
}

are_all_pr_repos_public() {
    REPO_IS_PRIVATE="true"
    print_red '\n%s\n' "Testing if repos specified in pr_branches are all public" >&2
    PR_BRANCHES="$*"
    for i in $PR_BRANCHES; do
        echo "Testing URL: ${i}" >&2
        user_slash_repo=$(echo "$i" | sed -r 's/.*github\.com\///g' | sed -r s'/\/tree.*//g' | sed -r 's/\/pull.*//g')
        REPO_IS_PUBLIC=$(is_repo_public "$user_slash_repo")
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

check_github_next_steps() {
    PUBLIC_REPO_STATUS=$1
    NEXT_STEP=0
    if [[ $PUBLIC_REPO_STATUS == "403" ]]; then
        printf "%s" 
        print_red "WARNING: Rate limit exceeded for github api requests." >&2
        printf "%s\n"
        printred " It is not currently possible to confirm whether all the URLs specified in PR_BRANCHES belong to public repos" >&2
        printf "%s\n" 
        printred "(Rate limits only last for 60 minutes, if you are unsure then please try again later)" >&2
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

confirm() {
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

handle_pr_branches() {
    if [[ $extra_vars == *"pr_branches="* ]]; then
        PR_BRANCHES="$(echo "$extra_vars" | sed -r 's/.*pr_branches=//g' | sed -r 's/;.*//g')"
        ARE_ALL_REPOS_PUBLIC=$(are_all_pr_repos_public "$PR_BRANCHES")
        NEXT_STEPS=$(check_github_next_steps "${ARE_ALL_REPOS_PUBLIC}")
        if [[ $NEXT_STEPS == "exit" ]]; then
            exit 0
        elif [[ $NEXT_STEPS == "skip_check" ]]; then
            print_yellow "Skipping ssh auth and github login"
            formatted_extra_vars="$formatted_extra_vars skip_git_ssh_auth=true"
        elif [[ $NEXT_STEPS == "all_public" ]]; then
            print_yellow "All pr_branch URLs are public, continuing without ssh authentication"
            formatted_extra_vars="$formatted_extra_vars skip_git_ssh_auth=true"
        else
            formatted_extra_vars="$formatted_extra_vars skip_git_ssh_auth=false"
            print_yellow " -------------------------------------------------------------------------------------"
            print_yellow "Testing SSH connection to Github with ssh -oStrictHostKeyChecking=no -T git@github.com"
            print_yellow "Using SSH key from $github_ssh_private_key_path"
            ssh_test=$(ssh -oStrictHostKeyChecking=no -T git@github.com 2>&1 &)
            if [[ "$ssh_test" == *"You've successfully authenticated"* ]]; then
                print_green " ---------------------------------"
                print_green "Github SSH key successfully added!"
                print_green " ---------------------------------"
            else
                if [[ -z ${read_input} ]]; then
                    read_input="github_email"
                else
                    read_input=$read_input",github_email"
                fi
                while sudo fuser /var/lib/dpkg/lock >/dev/null 2>&1; do
                    print_yellow "Waiting for apt-get install file lock..."
                    sleep 1
                done
                sudo apt-get install -y xclip
                print_green "xclip installed"
            fi
            IFS=',' read -ra inputdata <<< "$read_input"
            for i in "${inputdata[@]}"; do
                print_yellow "Data input for" 
                printf "$i"
                read -r input_data
                if [[ "${i}" = "github_email" ]]; then
                    if [[ ! -f "$github_ssh_public_key_path" ]]; then
                        ssh-keygen -t rsa -b 4096 -q -C "$github_email" -N "" -f "${HOME}"/.ssh/id_rsa
                    fi
                    eval "$(ssh-agent -s)"
                    ssh-add "$github_ssh_private_key_path"
                    xclip -sel clip < "$github_ssh_public_key_path"
                    print_yellow " ----------------------------------------------------------------------------------------------------"
                    print_yellow "There is an ssh public key in $github_ssh_public_key_path"
                    print_yellow "xclip is installed and public ssh key is copied into clipboard"
                    print_yellow "Right-click the URL below (don't copy the URL since your clipboard has the ssh key)"
                    print_yellow "Select Open Link and follow the steps from number 2 onwards:"
                    print_yellow "https://docs.github.com/en/github/authenticating-to-github/adding-a-new-ssh-key-to-your-github-account"
                    print_yellow " ----------------------------------------------------------------------------------------------------"
                    print_yellow "Confirm if you have added the SSH key to your Github account (y/n):"
                    read -r ssh_key_added
                    if [[ "$ssh_key_added" == "y" ]]; then
                        ssh_test=$(ssh -oStrictHostKeyChecking=no -T git@github.com 2>&1 &)
                        if [[ "$ssh_test" == *"You've successfully authenticated"* ]]; then
                            print_green " ---------------------------------"
                            print_green "Github SSH key successfully added!"
                            print_green " ---------------------------------"
                        else
                            print_red " ----------------------------------------------------------------------------------------------------"
                            print_red "Github SSH authentication failed with message: $ssh_test"
                            print_red " ----------------------------------------------------------------------------------------------------"
                            exit 1
                        fi
                    else
                        print_red "You have specified pr_branches but haven't added a Github SSH key"
                        print_red "Unable to proceed. See the link below"
                        print_red "https://docs.github.com/en/github/authenticating-to-github/adding-a-new-ssh-key-to-your-github-account"
                        exit 1
                    fi
                fi
                formatted_extra_vars="$formatted_extra_vars $i=$input_data"
            done
        fi
    fi
}

handle_secure_data() {
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
}

install_packages() {
    print_yellow ""
    print_yellow " ---------------------------------"
    print_yellow " |   Installing needed packages  |"
    print_yellow " ---------------------------------"
    print_yellow ""

    while (sudo fuser /var/lib/apt/lists/lock >/dev/null 2>&1) || (sudo fuser /var/lib/dpkg/lock >/dev/null 2>&1); do
        print_yellow "Waiting for apt-get update file lock..."
        sleep 1
    done
    sudo apt-get update
    sudo apt-get install -y git jq curl lsb-release libyaml-dev libssl-dev libffi-dev sshpass
    print_green "Packages installed : git jq curl lsb-release libyaml-dev libssl-dev libffi-dev sshpass"
    sudo chown "$USER":"$USER" "$AURORA_HOME" || true
    sudo rm -rf "$AURORA_HOME"

    git clone --depth 1 -b "${aurora_tools_branch}" https://github.com/shadow-robot/aurora.git "$AURORA_HOME"
    print_green "Aurora tools cloned"
}

run_ansible() {
    print_yellow ""
    print_yellow " -------------------"
    print_yellow " | Running Ansible |"
    print_yellow " -------------------"
    print_yellow ""

    pushd "$AURORA_HOME"

    export PYTHONNOUSERSITE=1
    source $AURORA_HOME/bin/conda_utils.sh
    export PYTHONPATH="${miniconda_install_location}/lib/python3.8/site-packages:${miniconda_install_location}/bin"

    create_conda_ws
    fetch_pip_files
    fetch_ansible_files
    install_pip_packages

    # WSL specific this is not supported. This is a workaround to start docker service in WSL
    if grep -q "microsoft" /proc/version  && grep -iq "wsl" /proc/version; then
        pip install pyopenssl --upgrade
        WSL_START_DOCKER_COMMAND="wsl.exe --distribution "${WSL_DISTRO_NAME}" --user root --exec /usr/sbin/service docker start"
        if [[ $(which docker | wc -l) -gt 0 ]]; then
            if service docker status 2>&1 | grep -q "is not running"; then
                ${WSL_START_DOCKER_COMMAND}
            fi
        fi
        if [[ $(cat ~/.bashrc  | grep -c "${WSL_START_DOCKER_COMMAND}") -eq 0 ]]; then
            echo "$WSL_START_DOCKER_COMMAND" >> ~/.bashrc
        fi
    fi

    if [[ "${AURORA_LIMIT}" != "all" ]]; then
        VERBOSITY="-${VERBOSITY} --limit ${AURORA_LIMIT}"
    fi

    if [[ "${PLAYBOOK}" = "server_and_nuc_deploy" ]]; then
        if [[ "${aurora_inventory}" = "" ]]; then
            aurora_inventory="ansible/inventory/server_and_nuc/production"
        else
            aurora_inventory="ansible/inventory/server_and_nuc/${aurora_inventory}"
        fi
        VERBOSITY="${VERBOSITY} --ask-vault-pass"
    
        print_yellow ""
        print_yellow " ---------------------------------------------------"
        print_yellow " |                 VAULT password:                 |"
        print_yellow " | Enter the VAULT password provided by Shadow     |"
        print_yellow " ---------------------------------------------------"
        print_yellow ""
    
    elif [[ "${PLAYBOOK}" = "teleop_deploy" ]]; then
        VERBOSITY="${VERBOSITY} --ask-vault-pass"
        if [[ "${aurora_inventory}" = "" ]]; then
            aurora_inventory="ansible/inventory/teleop/production"
        else
            aurora_inventory="ansible/inventory/teleop/${aurora_inventory}"
        fi

        print_yellow ""
        print_yellow " ---------------------------------------------------"
        print_yellow " |                 VAULT password:                 |"
        print_yellow " | Enter the VAULT password provided by Shadow     |"
        print_yellow " ---------------------------------------------------"
        print_yellow ""
    else
        aurora_inventory="ansible/inventory/${aurora_inventory}"
        VERBOSITY="${VERBOSITY} --ask-become-pass"
        print_yellow ""
        print_yellow " --------------------------------------------"
        print_yellow " |             BECOME password:             |"
        print_yellow " | Enter the sudo password of this computer |"
        print_yellow " --------------------------------------------"
        print_yellow ""
    fi

    ansible_executable="${miniconda_install_location}/bin/ansible-playbook"
    if [[ ! -f "${ansible_executable}" ]]; then
        ansible_executable=ansible-playbook
    fi
    ansible_basic_executable="${miniconda_install_location}/bin/ansible"
    if [[ ! -f "${ansible_basic_executable}" ]]; then
        ansible_basic_executable=ansible
    fi
    fi

    ansible_galaxy_executable="${miniconda_install_location}/bin/ansible-galaxy"
    if [[ ! -f "${ansible_galaxy_executable}" ]]; then
        ansible_galaxy_executable=ansible-galaxy
    fi

    "${ansible_basic_executable}" --version
    install_ansible_collections "${ansible_galaxy_executable}"

    if [[ "${PLAYBOOK}" = "server_and_nuc_deploy" ]]; then
        if [[ $extra_vars != *"router=true"* && $extra_vars != *"product=arm_"* ]]; then
            "${ansible_executable}" -v -i "ansible/inventory/local/dhcp" "ansible/playbooks/dhcp.yml" --extra-vars "$formatted_extra_vars"
            print_green ""
            print_green " ----------------------------------------------------------------------"
            print_green " |    DHCP network ready! Proceeding with server and nuc playbook      |"
            print_green " ----------------------------------------------------------------------"
            print_green ""
        fi
    fi

    # Run the ansible-playbook command with the correct flags
    "${ansible_executable}" -${VERBOSITY} -i "${aurora_inventory}" "ansible/playbooks/${PLAYBOOK}.yml" --extra-vars "$formatted_extra_vars"

    popd

    echo ""
    echo " ------------------------------------------------"
    echo " |            Operation completed               |"
    echo " ------------------------------------------------"
    echo ""
}

main() {
    check_invalid_input "$@"
    set_variables "$@"
    check_variable_syntax "$@"
    format_extra_vars "$@"
    print_startup_message
    handle_pr_branches
    handle_secure_data
    install_packages
    run_ansible
}

main "$@"