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
set -o pipefail # fail on errors within pipelines

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color
BOLD='\033[1m'
LOG_DIR="/tmp/aurora_install_logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/install_$(date +%Y%m%d_%H%M%S).log"

script_name="bash <(curl -Ls bit.ly/run-aurora)"

command_usage_message="Command usage: ${script_name} <playbook name> [--branch <name>] [--inventory <name>]"
command_usage_message="${command_usage_message} [--limit <rules>]"
command_usage_message="${command_usage_message} [<parameter>=<value>] [<parameter>=<value>] ... [<parameter>=<value>]"


log_message() {
    echo "$(date +'%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}


cleanup() {
    log_message "Executing cleanup operations."
    log_message "Cleanup finished."
}

show_error() {
    local message="$1"
    local show_log="${2:-true}"

    # Log the error message itself first
    log_message "ERROR: $message"

    echo -e "\n${RED}╔════ ERROR ════${NC}"
    echo -e "${RED}║${NC} $message"
    echo -e "${RED}╚═══════════════${NC}"

    if [[ "$show_log" == "true" && -f "$LOG_FILE" ]]; then
        echo -e "\n${YELLOW}Last few lines of log:${NC}"
        echo "----------------------------------------"
        tail -n 10 "$LOG_FILE" | grep -v "password for" | while IFS= read -r line; do
            line=$(echo "$line" | sed -E 's/\[[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}\] //')
            echo "   #     $line"
        done
        echo "----------------------------------------"
        echo -e "\nFull logs available at: ${BOLD}$LOG_FILE${NC}"
    fi
    cleanup
    exit 1
}

log_message "Script started. Name: ${script_name}"
log_message "Command line arguments: $@"

if [[ $# -lt 2 ]]; then 
    show_error "Insufficient arguments provided.\n${command_usage_message}" "false"
fi

# Some molecule tests install to `/home/...` (no user account)
if [ -z $USER ]; then
    if [ -z $MY_USERNAME ]; then
        HOME='/home'
        log_message "USER not set, MY_USERNAME not set, setting HOME to /home"
    fi
fi

aurora_home=/tmp/aurora

playbook=$1
aurora_limit=all
shift

log_message "Parsing command line options..."
while [[ $# -gt 0 ]]; do # 
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
        *) # This will now capture extra_vars
        break
        ;;
    esac
done
log_message "Finished parsing command line options."


if [[ "${playbook}" = "server_and_nuc_deploy" || "${playbook}" = "teleop_deploy" ]]; then
    if [[ -z ${read_secure} ]]; then
        read_secure="sudo_password"
    else
        read_secure=$read_secure",sudo_password"
    fi
    log_message "Playbook type requires sudo_password; updated read_secure: ${read_secure}"
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
log_message "Final parameters: Playbook: ${playbook}, Branch: ${aurora_tools_branch}, Inventory: ${aurora_inventory}, Limit: ${aurora_limit}"

echo "================================================================="
echo "|                                                               |"
echo "|                 Shadow Ansible bootstraper                    |"
echo "|                                                               |"
echo "================================================================="
echo ""
echo "Possible options: "
echo "  * --branch            Branch or tag of aurora to use. Master by default. Can be a release tag, e.g. v1.0.0"
echo "  * --inventory         Inventory of servers to use (local by default)"
echo "  * --limit             Run a playbook against one or more members of that group (all by default)"
echo "  * --read-input        Prompt for input(s) required by some playbooks (e.g. docker_username,github_login)"
echo "  * --read-secure       Prompt for password(s) required by some playbooks (e.g. sudo_password,docker_password,git_password)"
echo ""
echo "Example: ${script_name} docker_deploy --branch F#SRC-2603_add_ansible_bootstrap --inventory local product=hand_e"
echo ""
echo "playbook     = ${playbook}"
echo "branch       = ${aurora_tools_branch}"
echo "inventory    = ${aurora_inventory}"
echo "limit        = ${aurora_limit}"
echo "read_input   = ${read_input}"
echo "read_secure  = ${read_secure}"

export ANSIBLE_ROLES_PATH="${aurora_home}/ansible/roles"
export ANSIBLE_CALLBACK_PLUGINS="${HOME}/.ansible/plugins/callback:/usr/share/ansible/plugins/callback:${aurora_home}/ansible/playbooks/callback_plugins"
export ANSIBLE_COLLECTIONS_PATHS="${aurora_home}/ansible/collections:${HOME}/.ansible/collections:/usr/share/ansible/collections"
export ANSIBLE_STDOUT_CALLBACK="custom_retry_runner"

extra_vars=$* # All remaining arguments are extra_vars
log_message "Raw extra_vars: ${extra_vars}"
if [[ $extra_vars == *":="* ]]; then
    error_detail="All aurora variable assignments should be done with just = not :=. You entered: ${extra_vars}. Please fix the syntax and try again."
    show_error "${error_detail}\n\n${command_usage_message}" "false"
fi


old_IFS=$IFS
IFS=";"
formatted_extra_vars=""
for extra_var_pair in $extra_vars; do # $extra_vars should be space separated "key=value" "key2=value with space"
    variable="${extra_var_pair%%=*}" 
    value="${extra_var_pair#*=}"    
    if [[ "$value" == *' '* && ! ("$value" == \'*\' || "$value" == \"*\") ]]; then # Avoid double quoting
        value="'$value'"
    fi
    if [[ $formatted_extra_vars == "" ]]; then
        formatted_extra_vars="$variable=$value"
    else
        formatted_extra_vars="$formatted_extra_vars $variable=$value"
    fi
done
IFS=${old_IFS}
log_message "Formatted extra_vars: ${formatted_extra_vars}"


is_repo_public() {
    local user_slash_repo=$1
    log_message "Checking public status of GitHub repo: ${user_slash_repo}"
    ERROR_OUTPUT=$(curl -fsS "https://api.github.com/repos/${user_slash_repo}" 2>&1 >/dev/null) # Capture stderr
    CURL_EXIT_CODE=$?
    if [ ${CURL_EXIT_CODE} -eq 0 ]; then
        log_message "The GitHub repo ${user_slash_repo} exists and is accessible."
        echo "true"
    else
        log_message "curl failed with exit code ${CURL_EXIT_CODE} for repo ${user_slash_repo}. Error: ${ERROR_OUTPUT}"
        if [[ "${ERROR_OUTPUT}" == *"API rate limit exceeded"* || "${ERROR_OUTPUT}" == *"error: 403"* ]]; then
            echo "403"
        else
            log_message "Error: no GitHub repo ${user_slash_repo} found or other curl error."
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
    REPO_IS_PRIVATE="true" # Assume all are public initially
    log_message "Testing if repos specified in pr_branches are all public."
    PR_BRANCHES_TO_CHECK="$@" # Use different var name to avoid conflict
    for i in $PR_BRANCHES_TO_CHECK; do
        log_message "Testing URL: ${i}"
        user_slash_repo=$(echo $i | sed -r 's/.*github\.com\///g' | sed -r 's/\/tree.*//g' | sed -r 's/\/pull.*//g')
        REPO_IS_PUBLIC_STATUS=$(is_repo_public "$user_slash_repo")
        if [[ $REPO_IS_PUBLIC_STATUS == "false" ]]; then
            REPO_IS_PRIVATE="false" # Found a non-public or non-existent repo
            log_message "Repo ${user_slash_repo} is not public or not found."
            break
        elif [[ $REPO_IS_PUBLIC_STATUS == "403" ]]; then
            REPO_IS_PRIVATE="403" # Rate limit hit
            log_message "Rate limit hit while checking repo ${user_slash_repo}."
            break
        fi
        log_message "Repo ${user_slash_repo} appears public."
    done
    echo "$REPO_IS_PRIVATE" # Will be true, false, or 403
}

check_github_next_steps(){
    PUBLIC_REPO_STATUS=$1
    NEXT_STEP=0
    if [[ $PUBLIC_REPO_STATUS == "403" ]]; then
        log_message "GitHub API rate limit exceeded. Cannot confirm PR repo status."
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
        log_message "All PR repos are public."
        NEXT_STEP="all_public"
    else # false, meaning at least one repo is private or not found
        log_message "Not all PR repos are public, or one was not found. Will proceed to key generation."
        NEXT_STEP="generate_key"
    fi
    echo "$NEXT_STEP"
}

github_ssh_public_key_path="${HOME}/.ssh/id_rsa.pub"
github_ssh_private_key_path="${HOME}/.ssh/id_rsa"

if [[ $formatted_extra_vars == *"pr_branches="* ]]; then
    log_message "pr_branches parameter detected. Checking repo status..."
    PR_BRANCHES_VALUE=$(echo "$formatted_extra_vars" | sed -n 's/.*pr_branches=\([^[:space:]]*\).*/\1/p' | sed "s/^'//;s/'$//")
    log_message "Extracted PR_BRANCHES_VALUE: ${PR_BRANCHES_VALUE}"

    ARE_ALL_REPOS_PUBLIC=$(are_all_pr_repos_public "$PR_BRANCHES_VALUE") # Pass the value
    NEXT_STEPS=$(check_github_next_steps "${ARE_ALL_REPOS_PUBLIC}")

    if [[ $NEXT_STEPS == "exit" ]]; then
        log_message "User chose to exit during GitHub SSH check."
        echo "Exiting as per user request."
        exit 0
    elif [[ $NEXT_STEPS == "skip_check" ]];then
        log_message "Skipping SSH auth and GitHub login for PR branches as per user choice or rate limit."
        echo "Skipping ssh auth and github login"
        formatted_extra_vars="$formatted_extra_vars skip_git_ssh_auth=true"
    elif [[ $NEXT_STEPS == "all_public" ]]; then
        log_message "All pr_branch URLs are public, continuing without ssh authentication setup."
        echo "All pr_branch URLs are public, continuing without ssh authentication"
        formatted_extra_vars="$formatted_extra_vars skip_git_ssh_auth=true"
    else # generate_key
        log_message "Proceeding with SSH key generation/check for GitHub."
        formatted_extra_vars="$formatted_extra_vars skip_git_ssh_auth=false"
        echo " -------------------------------------------------------------------------------------"
        log_message "Testing SSH connection to Github with ssh -oStrictHostKeyChecking=no -T git@github.com"
        echo "Testing SSH connection to Github with ssh -oStrictHostKeyChecking=no -T git@github.com"
        echo "Using SSH key from $github_ssh_private_key_path"
        ssh_test_output=$(ssh -o BatchMode=yes -o StrictHostKeyChecking=no -T git@github.com 2>&1)
        ssh_test_exit_code=$?
        log_message "SSH test exit code: ${ssh_test_exit_code}. Output: ${ssh_test_output}"

        if [[ $ssh_test_exit_code -eq 1 && "$ssh_test_output" == *"successfully authenticated"* ]]; then # GitHub SSH T test returns 1 on success
            log_message "GitHub SSH key successfully authenticated."
            echo " ---------------------------------"
            echo "Github SSH key successfully added!"
            echo " ---------------------------------"
        else
            log_message "GitHub SSH authentication failed or key not yet trusted. Prompting for setup."
            if [[ -z ${read_input} ]]; then
                read_input="github_email"
            else
                read_input=$read_input",github_email"
            fi
            log_message "Waiting for apt-get lock to install xclip..."
            while sudo fuser /var/lib/dpkg/lock >/dev/null 2>&1 || sudo fuser /var/lib/dpkg/lock-frontend >/dev/null 2>&1 || sudo fuser /var/lib/apt/lists/lock >/dev/null 2>&1; do
                echo "Waiting for apt-get install file lock..."
                sleep 1
            done
            log_message "Installing xclip..."
            if ! sudo apt-get install -y xclip >> "$LOG_FILE" 2>&1; then
                show_error "Failed to install xclip. This is needed for GitHub SSH key setup."
            fi
            log_message "xclip installed."
        fi
    fi 
fi 

if [[ -n "$read_input" ]]; then
    log_message "Processing --read-input: ${read_input}"
    IFS=',' read -ra inputdata <<< "$read_input"
    for i in "${inputdata[@]}"; do
        printf "Data input for $i:"
        read -r input_data_value # Renamed variable to avoid conflict
        if [[ "${i}" = "github_email" ]]; then
            github_email_val="$input_data_value" # Store it for ssh-keygen
            log_message "Received github_email: ${github_email_val}"
            if [[ ! -f "$github_ssh_public_key_path" ]]; then
                log_message "SSH key not found at ${github_ssh_public_key_path}. Generating new key."
                if ! ssh-keygen -t rsa -b 4096 -q -C "$github_email_val" -N "" -f "${github_ssh_private_key_path}" >> "$LOG_FILE" 2>&1; then
                     show_error "Failed to generate SSH key for GitHub."
                fi
                log_message "SSH key generated."
            fi
            log_message "Starting ssh-agent and adding key."
            eval "$(ssh-agent -s)" >> "$LOG_FILE" 2>&1
            if ! ssh-add "$github_ssh_private_key_path" >> "$LOG_FILE" 2>&1; then
                show_error "Failed to add SSH key to ssh-agent."
            fi
            if ! xclip -sel clip < "$github_ssh_public_key_path"; then
                show_error "Failed to copy SSH public key to clipboard using xclip."
            fi
            log_message "SSH public key copied to clipboard."
            echo " ----------------------------------------------------------------------------------------------------"
            echo "There is an ssh public key in $github_ssh_public_key_path"
            echo "xclip is installed and public ssh key is copied into clipboard"
            echo "Right-click the URL below (don't copy the URL since your clipboard has the ssh key)"
            echo "Select Open Link and follow the steps from number 2 onwards:"
            echo "https://docs.github.com/en/github/authenticating-to-github/adding-a-new-ssh-key-to-your-github-account"
            echo " ----------------------------------------------------------------------------------------------------"
            
            ssh_key_added_confirm=""
            while [[ "$ssh_key_added_confirm" != "y" ]]; do
                printf "Confirm if you have added the SSH key to your Github account (y/n):"
                read -r ssh_key_added_confirm
                if [[ "$ssh_key_added_confirm" == "n" ]]; then
                    show_error "User indicated SSH key was not added to GitHub. Cannot proceed with PR branches that require authentication."
                elif [[ "$ssh_key_added_confirm" != "y" ]]; then
                    echo "Please answer 'y' or 'n'."
                fi
            done

            log_message "User confirmed SSH key added to GitHub. Verifying..."
            ssh_test_after_add_output=$(ssh -o BatchMode=yes -o StrictHostKeyChecking=no -T git@github.com 2>&1)
            ssh_test_after_add_exit_code=$?
            log_message "SSH test after add exit code: ${ssh_test_after_add_exit_code}. Output: ${ssh_test_after_add_output}"

            if [[ $ssh_test_after_add_exit_code -eq 1 && "$ssh_test_after_add_output" == *"successfully authenticated"* ]]; then
                log_message "GitHub SSH key successfully authenticated after manual add."
                echo " ---------------------------------"
                echo "Github SSH key successfully added!"
                echo " ---------------------------------"
            else
                show_error "Github SSH authentication failed after user confirmation. Message: $ssh_test_after_add_output"
            fi
        fi
        formatted_extra_vars="$formatted_extra_vars $i=$input_data_value" # Use the new variable name
    done
    log_message "Updated formatted_extra_vars after read_input: ${formatted_extra_vars}"
fi


if [[ -n "$read_secure" ]]; then
    log_message "Processing --read-secure: ${read_secure}"
    IFS=',' read -ra securedata <<< "$read_secure"
    for i in "${securedata[@]}"; do
        printf "\nSecure data input for $i:"
        read -rs secure_data_value
        log_message "Received secure data for $i (value not logged)."
        while [[ "${i}" = "customer_key" && "${#secure_data_value}" -ne 40 ]]; do
            printf "\nSecure data input for $i is not valid\nIt should be 40 characters long\nYours was: ${#secure_data_value} characters long\nPlease enter a valid $i\n"
            printf "\nSecure data input for $i:"
            read -rs secure_data_value
            log_message "Re-entered secure data for $i (value not logged)."
        done
        formatted_extra_vars="$formatted_extra_vars $i=$secure_data_value" # Use new variable
    done
    log_message "Updated formatted_extra_vars after read_secure (values not logged)."
fi

echo ""
echo " ---------------------------------"
echo " |   Installing needed packages  |"
echo " ---------------------------------"
echo ""

log_message "Waiting for apt-get update lock..."
while (sudo fuser /var/lib/apt/lists/lock >/dev/null 2>&1) || (sudo fuser /var/lib/dpkg/lock >/dev/null 2>&1) || (sudo fuser /var/lib/dpkg/lock-frontend >/dev/null 2>&1) ; do
    echo "Waiting for apt-get update file lock..."
    sleep 1
done
log_message "Updating package lists (apt-get update)..."
if ! sudo apt-get update >> "$LOG_FILE" 2>&1; then
    show_error "apt-get update failed. Check $LOG_FILE for details."
fi
log_message "Package lists updated."

log_message "Waiting for apt-get install lock..."
while sudo fuser /var/lib/dpkg/lock >/dev/null 2>&1 || sudo fuser /var/lib/dpkg/lock-frontend >/dev/null 2>&1; do
    echo "Waiting for apt-get install file lock..."
    sleep 1
done
log_message "Installing base packages: git jq curl lsb-release libyaml-dev libssl-dev libffi-dev sshpass..."
REQUIRED_PACKAGES="git jq curl lsb-release libyaml-dev libssl-dev libffi-dev sshpass"
if ! sudo apt-get install -y $REQUIRED_PACKAGES >> "$LOG_FILE" 2>&1; then
    show_error "Failed to install one or more prerequisite packages ($REQUIRED_PACKAGES). Check $LOG_FILE."
fi
log_message "Base packages installed."

log_message "Setting ownership of $aurora_home (if it exists) and removing it."
sudo chown $USER:$USER $aurora_home || true # Allow failure if dir doesn't exist
sudo rm -rf "${aurora_home}"
log_message "$aurora_home removed."

log_message "Cloning aurora repository (branch: ${aurora_tools_branch}) into ${aurora_home}..."
# aurora_home_cloned_by_script="$aurora_home" # Set flag for potential cleanup
if ! git clone --depth 1 -b "${aurora_tools_branch}" https://github.com/shadow-robot/aurora.git "$aurora_home" >> "$LOG_FILE" 2>&1; then
    show_error "Failed to clone aurora repository from branch ${aurora_tools_branch}. Check $LOG_FILE."
fi
log_message "Aurora repository cloned successfully."

echo ""
echo " -------------------"
echo " | Running Ansible |"
echo " -------------------"
echo ""

pushd "$aurora_home" >> /dev/null # Silence pushd output from console

export PYTHONNOUSERSITE=1 # Ensure user site packages are not used for Conda
log_message "Sourcing conda_utils.sh from $aurora_home/bin/conda_utils.sh"
if ! source "$aurora_home/bin/conda_utils.sh" >> "$LOG_FILE" 2>&1; then # Capture output/errors
    show_error "Failed to source conda_utils.sh. Check $LOG_FILE."
fi
# miniconda_install_location should be defined in conda_utils.sh
export PYTHONPATH="${miniconda_install_location}/lib/python3.8/site-packages:${miniconda_install_location}/bin:${PYTHONPATH}"
log_message "PYTHONPATH set to: $PYTHONPATH"


log_message "Creating conda workspace via create_conda_ws..."
if ! create_conda_ws >> "$LOG_FILE" 2>&1; then
    show_error "Failed to create conda workspace using create_conda_ws. Check $LOG_FILE."
fi
log_message "Conda workspace created."

log_message "Fetching pip files via fetch_pip_files..."
if ! fetch_pip_files >> "$LOG_FILE" 2>&1; then
    show_error "Failed to fetch pip files using fetch_pip_files. Check $LOG_FILE."
fi
log_message "Pip files fetched."

log_message "Fetching ansible files via fetch_ansible_files..."
if ! fetch_ansible_files >> "$LOG_FILE" 2>&1; then
    show_error "Failed to fetch ansible files using fetch_ansible_files. Check $LOG_FILE."
fi
log_message "Ansible files fetched."

log_message "Installing pip packages via install_pip_packages..."
if ! install_pip_packages >> "$LOG_FILE" 2>&1; then
    show_error "Failed to install pip packages using install_pip_packages. Check $LOG_FILE."
fi
log_message "Pip packages installed."


# Fix for WSL
if grep -q "microsoft" /proc/version && grep -iq "wsl" /proc/version; then
    log_message "WSL detected. Applying WSL specific fixes."
    pip install pyopenssl --upgrade >> "$LOG_FILE" 2>&1
    WSL_START_DOCKER_COMMAND='wsl.exe --distribution "${WSL_DISTRO_NAME}" --user root --exec /usr/sbin/service docker start'
    if [[ $(which docker | wc -l) -gt 0 ]]; then
        if service docker status 2>&1 | grep -q "is not running"; then
            log_message "Docker service not running in WSL. Attempting to start."
            eval ${WSL_START_DOCKER_COMMAND} >> "$LOG_FILE" 2>&1 || log_message "Warning: WSL Docker start command encountered an issue."
        fi
    fi
    if [[ $(cat ~/.bashrc | grep "${WSL_START_DOCKER_COMMAND}" | wc -l) -eq 0 ]]; then
        log_message "Adding Docker start command to ~/.bashrc for WSL."
        echo "$WSL_START_DOCKER_COMMAND" >> ~/.bashrc
    fi
    log_message "WSL fixes applied."
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
    echo " |                VAULT password:                   |"
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
    echo " |                VAULT password:                   |"
    echo " | Enter the VAULT password provided by Shadow     |"
    echo " ---------------------------------------------------"
    echo ""
else
    aurora_inventory="ansible/inventory/${aurora_inventory}"
    ansible_flags="${ansible_flags} --ask-become-pass"
    echo ""
    echo " --------------------------------------------"
    echo " |              BECOME password:             |"
    echo " | Enter the sudo password of this computer |"
    echo " --------------------------------------------"
    echo ""
fi
log_message "Ansible inventory path set to: ${aurora_inventory}"
log_message "Ansible flags set to: ${ansible_flags}"

ansible_executable="${miniconda_install_location}/bin/ansible-playbook"
if [[ ! -f "${ansible_executable}" ]]; then
    log_message "Ansible playbook from Conda not found at ${ansible_executable}, falling back to system ansible-playbook."
    ansible_executable="ansible-playbook"
fi
ansible_basic_executable="${miniconda_install_location}/bin/ansible"
if [[ ! -f "${ansible_basic_executable}" ]]; then
    log_message "Ansible basic executable from Conda not found, falling back to system ansible."
    ansible_basic_executable="ansible"
fi
ansible_galaxy_executable="${miniconda_install_location}/bin/ansible-galaxy"
if [[ ! -f "${ansible_galaxy_executable}" ]]; then
    log_message "Ansible Galaxy from Conda not found, falling back to system ansible-galaxy."
    ansible_galaxy_executable="ansible-galaxy"
fi
log_message "Using ansible-playbook: $ansible_executable"
log_message "Using ansible: $ansible_basic_executable"
log_message "Using ansible-galaxy: $ansible_galaxy_executable"

install_ansible_collections() {
    local galaxy_exec="$1"
    local collections_dir
    collections_dir="${ANSIBLE_COLLECTIONS_PATHS%%:*}" # Get the first path
    mkdir -p "$collections_dir" || show_error "Failed to create collections directory: $collections_dir"

    log_message "Installing Ansible collection community.general into ${collections_dir}..."
    if ! "$galaxy_exec" collection install community.general -p "$collections_dir" >> "$LOG_FILE" 2>&1; then
        show_error "Failed to install Ansible collection community.general. Check $LOG_FILE."
    fi
    log_message "Installing Ansible collection community.docker into ${collections_dir}..."
    if ! "$galaxy_exec" collection install community.docker -p "$collections_dir" >> "$LOG_FILE" 2>&1; then
        show_error "Failed to install Ansible collection community.docker. Check $LOG_FILE."
    fi
    log_message "Installing Ansible collection amazon.aws (newer) or community.aws (older) into ${collections_dir}..."
    # Try amazon.aws first, then community.aws for compatibility
    if ! "$galaxy_exec" collection install amazon.aws -p "$collections_dir" >> "$LOG_FILE" 2>&1; then
        log_message "Failed to install amazon.aws, trying community.aws..."
        if ! "$galaxy_exec" collection install community.aws -p "$collections_dir" >> "$LOG_FILE" 2>&1; then
            show_error "Failed to install Ansible collection amazon.aws or community.aws. Check $LOG_FILE."
        fi
    fi
    log_message "Installing Ansible collection ansible.posix into ${collections_dir}..."
    if ! "$galaxy_exec" collection install ansible.posix -p "$collections_dir" >> "$LOG_FILE" 2>&1; then
        show_error "Failed to install Ansible collection ansible.posix. Check $LOG_FILE."
    fi
    log_message "Ansible collections installation attempt finished."
}

log_message "Checking Ansible version..."
if ! "${ansible_basic_executable}" --version >> "$LOG_FILE" 2>&1; then
    show_error "Failed to get ansible version. Is Ansible installed correctly? Check $LOG_FILE."
fi
log_message "$(${ansible_basic_executable} --version | head -n1)" # Log first line of version output

install_ansible_collections "${ansible_galaxy_executable}"


#configure DHCP before running the actual playbook
if [[ "${playbook}" = "server_and_nuc_deploy" ]]; then
    if [[ $formatted_extra_vars != *"router=true"* && $formatted_extra_vars != *"product=arm_"* ]]; then
        log_message "Configuring DHCP using dhcp.yml playbook..."
        echo "Executing: ${ansible_executable} -v -i \"ansible/inventory/local/dhcp\" \"ansible/playbooks/dhcp.yml\" --extra-vars \"$formatted_extra_vars\"" >> "$LOG_FILE"
        if ! "${ansible_executable}" -v -i "ansible/inventory/local/dhcp" "ansible/playbooks/dhcp.yml" --extra-vars "$formatted_extra_vars" 2>&1 | tee -a "$LOG_FILE"; then
            show_error "DHCP configuration playbook (dhcp.yml) failed. Check $LOG_FILE."
        fi
        log_message "DHCP configuration playbook completed."
        echo ""
        echo " ----------------------------------------------------------------------"
        echo " |     DHCP network ready! Proceeding with server and nuc playbook    |"
        echo " ----------------------------------------------------------------------"
        echo ""
    fi
fi

log_message "Executing main Ansible playbook: ${playbook} with inventory: ${aurora_inventory}"
log_message "Ansible command: ${ansible_executable} -v ${ansible_flags} -i \"${aurora_inventory}\" \"ansible/playbooks/${playbook}.yml\" --extra-vars \"$formatted_extra_vars\""
if ! "${ansible_executable}" -v ${ansible_flags} -i "${aurora_inventory}" "ansible/playbooks/${playbook}.yml" --extra-vars "$formatted_extra_vars" 2>&1 | tee -a "$LOG_FILE"; then
    show_error "Ansible playbook '${playbook}' failed. Check $LOG_FILE for details."
fi
log_message "Ansible playbook '${playbook}' execution attempt finished."
log_message "Operation completed successfully."
echo ""
echo " ------------------------------------------------"
echo " |            Operation completed               |"
echo " ------------------------------------------------"
echo ""
if [[ -f "$LOG_FILE" ]]; then
    echo -e "Full logs available at: ${BOLD}$LOG_FILE${NC}"
fi

exit 0