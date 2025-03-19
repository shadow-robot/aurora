#!/usr/bin/env bash

# Copyright 2022-2025 Shadow Robot Company Ltd.
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

# GUI mode flag (default to true)
USE_GUI=true
DEBUG_MODE=false

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Create log directory
LOG_DIR="/tmp/aurora_install_logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/install_$(date +%Y%m%d_%H%M%S).log"

# Cleanup function
cleanup() {
    echo -e "\n${RED}Installation cancelled by user${NC}"
    # Kill any background processes
    jobs -p | xargs -r kill
    # Clean up temporary files
    rm -f /tmp/vault_pass /tmp/sudo_pass
    exit 1
}

# Set up signal handling
trap cleanup SIGINT SIGTERM

# Get terminal dimensions
TERM_ROWS=$(tput lines)
TERM_COLS=$(tput cols)

# Calculate whiptail dimensions (75% of terminal size)
WHIP_ROWS=$((TERM_ROWS * 75 / 100))
WHIP_COLS=$((TERM_COLS * 75 / 100))

# Minimum sizes
MIN_ROWS=10
MIN_COLS=50
WHIP_ROWS=$((WHIP_ROWS > MIN_ROWS ? WHIP_ROWS : MIN_ROWS))
WHIP_COLS=$((WHIP_COLS > MIN_COLS ? WHIP_COLS : MIN_COLS))

# Message box heights
MSG_HEIGHT=$((WHIP_ROWS - 4))
GAUGE_HEIGHT=8

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
    # Only print debug messages if debug mode is enabled
    if [[ "$DEBUG_MODE" == "true" ]]; then
        echo "[DEBUG] $1" >&2
    fi
}

# Function to update progress
update_progress() {
    local percent="$1"
    local message="$2"
    echo "XXX"
    echo "$percent"
    echo "$message"
    echo "XXX"
}

# Terminal mode functions
term_echo() {
    local color="$1"
    local message="$2"
    echo -e "${color}${message}${NC}"
}

term_prompt() {
    local prompt="$1"
    local secure="${2:-false}"
    local input
    
    if [[ "$secure" == "true" ]]; then
        read -s -p "$prompt" input
        echo "" # New line after secure input
    else
        read -p "$prompt" input
    fi
    echo "$input"
}

# Function to show error message and exit
show_error() {
    local message="$1"
    local show_log="${2:-true}"
    
    echo -e "\n${RED}╔════ ERROR ════╗${NC}"
    echo -e "${RED}║${NC} $message"
    echo -e "${RED}╚═══════════════╝${NC}"
    
    if [[ "$show_log" == "true" && -f "$LOG_FILE" ]]; then
        echo -e "\n${YELLOW}Last few lines of log:${NC}"
        echo "----------------------------------------"
        # Process log lines to make them more readable
        tail -n 10 "$LOG_FILE" | grep -v "password for" | while IFS= read -r line; do
            # Remove timestamps from log lines
            line=$(echo "$line" | sed -E 's/\[[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}\] //')
            # Add proper indentation
            echo "  #     $line"
        done
        echo "----------------------------------------"
        echo -e "\nFull logs available at: ${BOLD}$LOG_FILE${NC}"
    fi
    
    if [[ "$USE_GUI" == "true" ]]; then
        whiptail --title "Error" --msgbox "Error: ${message}\n\nCheck the logs at: $LOG_FILE\n\nInstallation cannot continue." $((MSG_HEIGHT - 2)) $WHIP_COLS
    fi
    
    log_message "ERROR: $message"
    cleanup
}

# Function to show warning message
show_warning() {
    local message="$1"
    if [[ "$USE_GUI" == "true" ]]; then
        whiptail --title "Warning" --msgbox "Warning: ${message}" $((MSG_HEIGHT - 2)) $WHIP_COLS
    else
        term_echo "$YELLOW" "Warning: ${message}"
    fi
    log_message "WARNING: $message"
}

# Function to get secure input
get_secure_input() {
    local prompt="$1"
    local password
    
    if [[ "$USE_GUI" == "true" ]]; then
        password=$(whiptail --title "Secure Input" --passwordbox "\n${prompt}" $((MSG_HEIGHT - 2)) $WHIP_COLS 3>&1 1>&2 2>&3)
    else
        password=$(term_prompt "${prompt}: " true)
    fi
    echo "$password"
}

# Function to show progress
show_progress() {
    local percent="$1"
    local message="$2"
    local detail="${3:-}"
    local force_newline="${4:-false}"
    
    if [[ "$USE_GUI" == "true" ]]; then
        update_progress "$percent" "$message"
    else
        # Only clear line if we're not forcing a newline
        if [[ "$force_newline" != "true" ]]; then
            printf "\r\033[K"
        fi
        
        # Show progress bar
        local width=50
        local completed=$((width * percent / 100))
        local remaining=$((width - completed))
        
        printf "["
        printf "%${completed}s" | tr ' ' '='
        printf ">"
        printf "%${remaining}s" | tr ' ' ' '
        printf "] %3d%%" "$percent"
        
        # Show message
        printf " %s" "$message"
        
        # Show detail if provided
        if [[ -n "$detail" ]]; then
            printf "\n    → %s" "$detail"
        fi
        
        # Add newline if requested
        if [[ "$force_newline" == "true" ]]; then
            printf "\n"
        fi
        
        # Force flush output
        if [ -t 1 ]; then
            stty -icanon min 0 time 0
            dd count=1 2>/dev/null
            stty icanon
        fi
    fi
}

# Function to run command and show progress
run_command() {
    local cmd="$1"
    local msg="$2"
    local progress="$3"
    local needs_sudo="${4:-false}"
    local ignore_errors="${5:-false}"
    local show_output="${6:-false}"
    local timeout="${7:-1800}"  # 30 minute default timeout
    local in_subshell="${8:-false}"
    
    # Debug output
    log_message "Running command: $cmd"
    log_message "Current PATH: $PATH"
    log_message "Current conda env: $CONDA_PREFIX"
    
    # Show initial progress
    show_progress "$progress" "$msg"
    log_message "Running: $cmd"
    
    # Create a temporary file for the exit status
    local exit_status_file=$(mktemp)
    local output_file=$(mktemp)
    
    if [[ "$in_subshell" == "true" ]]; then
        # Run in a subshell to preserve environment
        (
            # Run the command
            if [[ "$needs_sudo" == "true" ]]; then
                echo "$SUDO_PASSWORD" | sudo -S bash -c "$cmd" 2>&1 || echo $? > "$exit_status_file"
            else
                eval "$cmd" 2>&1 || echo $? > "$exit_status_file"
            fi
        ) | tee -a "$LOG_FILE" "$output_file" ${show_output:+/dev/tty} >/dev/null
    else
        # Run the command with timeout in background
        if [[ "$USE_GUI" != "true" && "$show_output" == "true" ]]; then
            # For commands where we want to show real-time output
            if [[ "$needs_sudo" == "true" ]]; then
                (timeout "$timeout" bash -c "echo \"$SUDO_PASSWORD\" | sudo -S bash -c \"$cmd\"" 2>&1 || echo $? > "$exit_status_file") | tee -a "$LOG_FILE" "$output_file"
            else
                (timeout "$timeout" bash -c "$cmd" 2>&1 || echo $? > "$exit_status_file") | tee -a "$LOG_FILE" "$output_file"
            fi
        else
            # For commands where we just want to log output
            if [[ "$needs_sudo" == "true" ]]; then
                (timeout "$timeout" bash -c "echo \"$SUDO_PASSWORD\" | sudo -S bash -c \"$cmd\"" 2>&1 || echo $? > "$exit_status_file") | tee -a "$LOG_FILE" "$output_file" >/dev/null
            else
                (timeout "$timeout" bash -c "$cmd" 2>&1 || echo $? > "$exit_status_file") | tee -a "$LOG_FILE" "$output_file" >/dev/null
            fi
        fi
    fi
    
    # Show periodic updates for long-running commands
    local last_shown=""
    while kill -0 $! 2>/dev/null; do
        local last_line=$(tail -n 1 "$output_file" | tr -d '\n' | cut -c1-50)
        if [[ -n "$last_line" && "$last_line" != "$last_shown" ]]; then
            show_progress "$progress" "$msg" "$last_line"
            last_shown="$last_line"
        fi
        sleep 1
    done
    
    wait $! || true
    local ret=$?
    
    # Check if we have a timeout or other error
    if [[ -s "$exit_status_file" ]]; then
        ret=$(cat "$exit_status_file")
    fi
    
    # Cleanup temporary files
    rm -f "$exit_status_file" "$output_file"
    
    # Handle different types of failures
    if [ $ret -eq 124 ]; then
        show_error "Command timed out after $((timeout/60)) minutes: $msg" true
        return 1
    elif [ $ret -ne 0 ] && [ "$ignore_errors" != "true" ]; then
        # Show more context in error messages
        local error_context=$(tail -n 5 "$LOG_FILE" | grep -v "password for" | tr '\n' ' ')
        show_error "Failed: $msg\nLast output: $error_context" true
        return 1
    fi
    
    # Show completion message with newline
    show_progress "$progress" "$msg" "Completed successfully" true
    return 0
}

# Install whiptail if not present
ensure_whiptail() {
    if ! command -v whiptail >/dev/null 2>&1; then
        echo "Installing whiptail..."
        sudo apt-get update && sudo apt-get install -y whiptail
    fi
}

# Show welcome screen
show_welcome() {
    local welcome_message="\
    Welcome to Shadow Robot Ansible Installer
    ========================================

    This installer will help you set up and configure
    Shadow Robot software components.

    - Automated installation process
    - Secure configuration
    - Expert deployment options"

    if [[ "$USE_GUI" == "true" ]]; then
        whiptail --title "Shadow Robot Ansible Installer" --msgbox "$welcome_message" $MSG_HEIGHT $WHIP_COLS
    else
        term_echo "$BLUE" "$welcome_message"
        echo ""
    fi
}

script_name="bash <(curl -Ls bit.ly/run-aurora)"

command_usage_message="Command usage: ${script_name} <playbook name> [--branch <n>] [--inventory <n>]"
command_usage_message="${command_usage_message} [--limit <rules>] [--no-gui]"
command_usage_message="${command_usage_message} [<parameter>=<value>] [<parameter>=<value>] ... [<parameter>=<value>]"

# First, check for --no-gui and --debug flags anywhere in the arguments
for arg in "$@"; do
    if [[ "$arg" == "--no-gui" ]]; then
        USE_GUI=false
    elif [[ "$arg" == "--debug" ]]; then
        DEBUG_MODE=true
    fi
done

# Remove --no-gui and --debug from arguments if present
args=()
for arg in "$@"; do
    if [[ "$arg" != "--no-gui" && "$arg" != "--debug" ]]; then
        args+=("$arg")
    fi
done
set -- "${args[@]}"

# Process remaining arguments
while [[ $# -gt 1 ]]; do
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

# Only ensure whiptail if using GUI
if [[ "$USE_GUI" == "true" ]]; then
    ensure_whiptail
fi

# Show welcome screen if not in automated mode and GUI is enabled
if [ -t 1 ] && [[ "$USE_GUI" == "true" ]]; then
    show_welcome
fi

if [[ $# -lt 1 ]]; then
    if [[ "$USE_GUI" == "true" ]]; then
        whiptail --title "Error" --msgbox "Not enough arguments.\n\n${command_usage_message}" 12 78
    else
        term_echo "$RED" "Error: Not enough arguments.\n\n${command_usage_message}"
    fi
    exit 1
fi

# Parse command line arguments
playbook=$1
aurora_limit=all
shift

# Process extra vars
extra_vars=$*
if [[ $extra_vars == *":="* ]]; then
    whiptail --title "Error" --msgbox "All aurora variable assignments should be done with just = not :=\n\nYou entered: $extra_vars\n\nPlease fix the syntax and try again\n\n${command_usage_message}" 15 60
    exit 1
fi

# Handle spaces in extra vars
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

# Set default values
aurora_tools_branch=${aurora_tools_branch:-master}
if [[ "${playbook}" = "server_and_nuc_deploy" || "${playbook}" = "teleop_deploy" ]]; then
    aurora_inventory=${aurora_inventory:-""}
    read_secure=${read_secure:-"sudo_password"}
else
    aurora_inventory=${aurora_inventory:-"ansible/inventory/local/${playbook}"}
fi

# Show configuration summary
show_config() {
    local config_message="\
The following configuration will be used:

Playbook:     ${playbook}
Branch:       ${aurora_tools_branch}
Inventory:    ${aurora_inventory}
Limit:        ${aurora_limit}"

    if [[ "$USE_GUI" == "true" ]]; then
        whiptail --title "Configuration Summary" --msgbox "${config_message}\n\nPress OK to begin installation" 15 60
    else
        term_echo "$BLUE" "$config_message"
        echo ""
        term_prompt "Press Enter to begin installation..."
    fi
}

# Get all required passwords upfront
get_passwords() {
    # Get sudo password
    SUDO_PASSWORD=$(get_secure_input "Enter sudo password (will be used for all sudo operations):")
    [[ -z "$SUDO_PASSWORD" ]] && show_error "Sudo password is required"
    
    # Verify sudo password
    echo "$SUDO_PASSWORD" | sudo -S true >/dev/null 2>&1 || {
        show_error "Incorrect sudo password"
        exit 1
    }
    export SUDO_PASSWORD

    # Get vault/become password if needed
    if [[ "${playbook}" = "server_and_nuc_deploy" || "${playbook}" = "teleop_deploy" ]]; then
        VAULT_PASSWORD=$(get_secure_input "Enter the VAULT password provided by Shadow:")
        [[ -z "$VAULT_PASSWORD" ]] && show_error "Vault password is required"
        export VAULT_PASSWORD
    else
        # For non-server deployments, we'll reuse sudo password for become
        export ANSIBLE_BECOME_PASS="$SUDO_PASSWORD"
    fi
}

# Get all passwords before starting the installation
get_passwords

# Main installation process
if [[ "$USE_GUI" == "true" ]]; then
    {
        # Update package lists (ignore non-critical errors)
        if ! run_command "apt-get update" "Updating package lists..." "10" true true; then
            log_message "Warning: apt-get update completed with non-critical errors"
        fi

        # Install required packages
        progress=20
        for package in git jq xq curl lsb-release libyaml-dev libssl-dev libffi-dev sshpass; do
            if ! run_command "apt-get install -y $package" "Installing $package..." "$progress" true; then
                show_error "Failed to install $package"
            fi
            progress=$((progress + 5))
        done

        # Setup workspace
        if ! run_command "chown $USER:$USER /tmp/aurora || true; rm -rf /tmp/aurora" "Setting up workspace..." "60" true; then
            show_error "Failed to set up workspace"
        fi

        # Clone repository (no sudo needed)
        if ! run_command "git clone --depth 1 -b ${aurora_tools_branch} https://github.com/shadow-robot/aurora.git /tmp/aurora" "Cloning Aurora repository..." "70"; then
            show_error "Failed to clone repository"
        fi

        # Setup Python environment
        cd /tmp/aurora
        export PYTHONNOUSERSITE=1
        
        # Source conda utils first
        source bin/conda_utils.sh
        
        # Create conda environment and install packages
        if ! run_command "bash -c 'source bin/conda_utils.sh && create_conda_ws'" "Creating conda environment..." "75" false false true; then
            show_error "Failed to create conda environment"
        fi
        
        # Initialize and activate conda environment
        source "${miniconda_install_location}/etc/profile.d/conda.sh"
        eval "$(${miniconda_install_location}/bin/conda shell.bash hook)"
        if ! conda activate aurora_conda_ws; then
            show_error "Failed to activate conda environment. Try running 'conda info --envs' to see available environments."
        fi
        
        # Fetch and install packages
        if ! run_command "bash -c 'source bin/conda_utils.sh && source ${miniconda_install_location}/etc/profile.d/conda.sh && conda activate aurora_conda_ws && fetch_pip_files && fetch_ansible_files && install_pip_packages'" "Installing Python packages..." "80" false false true; then
            show_error "Failed to install Python packages"
        fi

        # Configure Ansible
        export ANSIBLE_ROLES_PATH="/tmp/aurora/ansible/roles"
        export ANSIBLE_CALLBACK_PLUGINS="${HOME}/.ansible/plugins/callback:/usr/share/ansible/plugins/callback:/tmp/aurora/ansible/playbooks/callback_plugins"
        export ANSIBLE_STDOUT_CALLBACK="custom_retry_runner"

        ansible_flags="-v"
        [[ "${aurora_limit}" != "all" ]] && ansible_flags="${ansible_flags} --limit ${aurora_limit}"

        # Configure authentication flags
        if [[ "${playbook}" = "server_and_nuc_deploy" || "${playbook}" = "teleop_deploy" ]]; then
            # Store vault password temporarily
            echo "$VAULT_PASSWORD" > /tmp/vault_pass
            ansible_flags="${ansible_flags} --vault-password-file /tmp/vault_pass"
        fi

        # Run Ansible playbook with real-time output (60 minute timeout)
        log_message "Running Ansible playbook"
        
        # Create a wrapper script to ensure proper environment setup
        cat > /tmp/run_playbook.sh << EOF
#!/bin/bash
set -e

# Source conda utils with full path
source "$(pwd)/bin/conda_utils.sh" || {
    echo "[ERROR] Failed to source conda_utils.sh"
    exit 1
}

# Initialize conda
source "${miniconda_install_location}/etc/profile.d/conda.sh" || {
    echo "[ERROR] Failed to source conda.sh"
    exit 1
}

# Deactivate any active environment
conda deactivate 2>/dev/null || true

# Activate our environment
conda activate ${conda_ws_name} || {
    echo "[ERROR] Failed to activate conda environment"
    exit 1
}

# Verify we're in the right environment
if [ "\$CONDA_PREFIX" != "${miniconda_install_location}/envs/${conda_ws_name}" ]; then
    echo "[ERROR] Wrong conda environment: \$CONDA_PREFIX"
    exit 1
fi

# Set up ansible executables with fallbacks
ansible_playbook_path="${miniconda_install_location}/bin/ansible-playbook"
if [[ ! -f "\$ansible_playbook_path" ]]; then
    echo "[WARNING] ansible-playbook not found in conda environment, falling back to system version"
    ansible_playbook_path=ansible-playbook
fi

# Process inventory path
inventory_path="\$1"
shift  # Remove the inventory argument

# Ensure inventory path is absolute
if [[ ! "\$inventory_path" =~ ^/ ]]; then
    inventory_path="\$(pwd)/\$inventory_path"
fi

# Process verbosity flag
verbosity=""
if [[ "\$1" == "-v" ]]; then
    verbosity="-v"
    shift
fi

# Get playbook path
playbook_path="\$1"
shift  # Remove the playbook path

# Process extra variables
extra_vars=""
while [[ \$# -gt 0 ]]; do
    if [[ "\$1" == "--extra-vars" ]]; then
        shift  # Skip the --extra-vars flag
        extra_vars="\$1"
        shift
    else
        # Format each variable as a proper ansible extra var
        if [[ -n "\$extra_vars" ]]; then
            extra_vars="\$extra_vars "
        fi
        extra_vars="\$extra_vars\$1"
        shift
    fi
done

# Only show debug output if debug mode is enabled
if [[ "${DEBUG_MODE}" == "true" ]]; then
    echo "[DEBUG] Using ansible-playbook: \$ansible_playbook_path"
    echo "[DEBUG] Inventory path: \$inventory_path"
    echo "[DEBUG] Playbook path: \$playbook_path"
    echo "[DEBUG] Verbosity: \$verbosity"
    echo "[DEBUG] Extra vars: \$extra_vars"
    echo "[DEBUG] CONDA_PREFIX: \$CONDA_PREFIX"
    echo "[DEBUG] PATH: \$PATH"
fi

# Execute ansible-playbook with proper arguments
exec "\$ansible_playbook_path" \$verbosity -i "\$inventory_path" "\$playbook_path" -e "\$extra_vars"
EOF
        chmod +x /tmp/run_playbook.sh
        
        if ! run_command "/tmp/run_playbook.sh ${aurora_inventory} -v ansible/playbooks/${playbook}.yml --extra-vars \"$formatted_extra_vars\"" "Running Ansible playbook..." "90" false false true 3600; then
            show_error "Ansible playbook execution failed" true
        fi
        
        # Clean up wrapper script
        rm -f /tmp/run_playbook.sh

        # Cleanup sensitive files
        rm -f /tmp/vault_pass
        
        # Deactivate conda environment
        conda deactivate

        # Cleanup sensitive data
        unset SUDO_PASSWORD VAULT_PASSWORD ANSIBLE_BECOME_PASS
        update_progress "100" "Installation complete!"
    } | whiptail --title "Installation Progress" --gauge "Starting installation..." $GAUGE_HEIGHT $WHIP_COLS 0
else
    # Run installation steps directly
    log_message "Starting installation in non-GUI mode"
    
    # Update package lists (ignore non-critical errors)
    if ! run_command "apt-get update" "Updating package lists..." "10" true true; then
        log_message "Warning: apt-get update completed with non-critical errors"
    fi
    
    # Install required packages
    progress=20
    for package in git jq curl lsb-release libyaml-dev libssl-dev libffi-dev sshpass; do
        if ! run_command "apt-get install -y $package" "Installing $package..." "$progress" true; then
            show_error "Failed to install $package"
        fi
        progress=$((progress + 5))
    done

    # Setup workspace
    log_message "Setting up workspace"
    if ! run_command "chown $USER:$USER /tmp/aurora || true; rm -rf /tmp/aurora" "Setting up workspace..." "60" true; then
        show_error "Failed to set up workspace"
    fi

    # Clone repository (no sudo needed)
    log_message "Cloning Aurora repository"
    if ! run_command "git clone --depth 1 -b ${aurora_tools_branch} https://github.com/shadow-robot/aurora.git /tmp/aurora" "Cloning Aurora repository..." "70"; then
        show_error "Failed to clone repository"
    fi

    # Setup Python environment
    cd /tmp/aurora
    export PYTHONNOUSERSITE=1
    
    # Source conda utils first
    log_message "Sourcing conda utils"
    source bin/conda_utils.sh
    
    # Create conda environment and install packages
    log_message "Creating conda environment"
    if ! run_command "source bin/conda_utils.sh && create_conda_ws" "Creating conda environment..." "75" false false true; then
        show_error "Failed to create conda environment"
    fi
    
    # Initialize and activate conda environment
    log_message "Initializing conda"
    source "${miniconda_install_location}/etc/profile.d/conda.sh"
    log_message "Running conda hook"
    eval "$(${miniconda_install_location}/bin/conda shell.bash hook)"
    log_message "Activating conda environment"
    if ! conda activate aurora_conda_ws; then
        show_error "Failed to activate conda environment. Try running 'conda info --envs' to see available environments."
    fi
    log_message "Conda environment activated: $CONDA_PREFIX"
    
    # Fetch and install packages
    log_message "Installing Python packages"
    if ! run_command "bash -c 'source bin/conda_utils.sh && source ${miniconda_install_location}/etc/profile.d/conda.sh && conda activate aurora_conda_ws && fetch_pip_files && fetch_ansible_files && install_pip_packages'" "Installing Python packages..." "80" false false true; then
        show_error "Failed to install Python packages"
    fi

    # Configure Ansible
    log_message "Configuring Ansible"
    export ANSIBLE_ROLES_PATH="/tmp/aurora/ansible/roles"
    export ANSIBLE_CALLBACK_PLUGINS="${HOME}/.ansible/plugins/callback:/usr/share/ansible/plugins/callback:/tmp/aurora/ansible/playbooks/callback_plugins"
    export ANSIBLE_STDOUT_CALLBACK="custom_retry_runner"

    ansible_flags="-v"
    [[ "${aurora_limit}" != "all" ]] && ansible_flags="${ansible_flags} --limit ${aurora_limit}"

    # Configure authentication flags
    if [[ "${playbook}" = "server_and_nuc_deploy" || "${playbook}" = "teleop_deploy" ]]; then
        # Store vault password temporarily
        echo "$VAULT_PASSWORD" > /tmp/vault_pass
        ansible_flags="${ansible_flags} --vault-password-file /tmp/vault_pass"
    fi

    # Run Ansible playbook with real-time output (60 minute timeout)
    log_message "Running Ansible playbook"
    
    # Create a wrapper script to ensure proper environment setup
    cat > /tmp/run_playbook.sh << EOF
#!/bin/bash
set -e

# Source conda utils with full path
source "$(pwd)/bin/conda_utils.sh" || {
    echo "[ERROR] Failed to source conda_utils.sh"
    exit 1
}

# Initialize conda
source "${miniconda_install_location}/etc/profile.d/conda.sh" || {
    echo "[ERROR] Failed to source conda.sh"
    exit 1
}

# Deactivate any active environment
conda deactivate 2>/dev/null || true

# Activate our environment
conda activate ${conda_ws_name} || {
    echo "[ERROR] Failed to activate conda environment"
    exit 1
}

# Verify we're in the right environment
if [ "\$CONDA_PREFIX" != "${miniconda_install_location}/envs/${conda_ws_name}" ]; then
    echo "[ERROR] Wrong conda environment: \$CONDA_PREFIX"
    exit 1
fi

# Set up ansible executables with fallbacks
ansible_playbook_path="${miniconda_install_location}/bin/ansible-playbook"
if [[ ! -f "\$ansible_playbook_path" ]]; then
    echo "[WARNING] ansible-playbook not found in conda environment, falling back to system version"
    ansible_playbook_path=ansible-playbook
fi

# Process inventory path
inventory_path="\$1"
shift  # Remove the inventory argument

# Ensure inventory path is absolute
if [[ ! "\$inventory_path" =~ ^/ ]]; then
    inventory_path="\$(pwd)/\$inventory_path"
fi

# Process verbosity flag
verbosity=""
if [[ "\$1" == "-v" ]]; then
    verbosity="-v"
    shift
fi

# Get playbook path
playbook_path="\$1"
shift  # Remove the playbook path

# Process extra variables
extra_vars=""
while [[ \$# -gt 0 ]]; do
    if [[ "\$1" == "--extra-vars" ]]; then
        shift  # Skip the --extra-vars flag
        extra_vars="\$1"
        shift
    else
        # Format each variable as a proper ansible extra var
        if [[ -n "\$extra_vars" ]]; then
            extra_vars="\$extra_vars "
        fi
        extra_vars="\$extra_vars\$1"
        shift
    fi
done

# Only show debug output if debug mode is enabled
if [[ "${DEBUG_MODE}" == "true" ]]; then
    echo "[DEBUG] Using ansible-playbook: \$ansible_playbook_path"
    echo "[DEBUG] Inventory path: \$inventory_path"
    echo "[DEBUG] Playbook path: \$playbook_path"
    echo "[DEBUG] Verbosity: \$verbosity"
    echo "[DEBUG] Extra vars: \$extra_vars"
    echo "[DEBUG] CONDA_PREFIX: \$CONDA_PREFIX"
    echo "[DEBUG] PATH: \$PATH"
fi

# Execute ansible-playbook with proper arguments
exec "\$ansible_playbook_path" \$verbosity -i "\$inventory_path" "\$playbook_path" -e "\$extra_vars"
EOF
    chmod +x /tmp/run_playbook.sh
    
    if ! run_command "/tmp/run_playbook.sh ${aurora_inventory} -v ansible/playbooks/${playbook}.yml --extra-vars \"$formatted_extra_vars\"" "Running Ansible playbook..." "90" false false true 3600; then
        show_error "Ansible playbook execution failed" true
    fi
    
    # Clean up wrapper script
    rm -f /tmp/run_playbook.sh

    # Cleanup sensitive files
    rm -f /tmp/vault_pass
    
    # Deactivate conda environment
    conda deactivate

    # Cleanup sensitive data
    unset SUDO_PASSWORD VAULT_PASSWORD ANSIBLE_BECOME_PASS
    update_progress "100" "Installation complete!"
fi

# Show completion status with more detail
show_completion() {
    local success="$1"
    local message
    
    if [[ "$success" == "true" ]]; then
        echo -e "\n${GREEN}╔════ SUCCESS ════╗${NC}"
        echo -e "${GREEN}║${NC} Installation completed successfully!"
        echo -e "${GREEN}╚════════════════╝${NC}"
        
        message="\
Installation completed successfully!

Your Shadow Robot software has been installed and configured.
You can now proceed with using the system.

Installation logs are available at: $LOG_FILE

For support, email: support@shadowrobot.com"
        
        if [[ "$USE_GUI" == "true" ]]; then
            whiptail --title "Installation Complete" --msgbox "$message" $MSG_HEIGHT $WHIP_COLS
        else
            echo -e "\n$message"
        fi
        
        echo -e "\nLogs available at: ${BOLD}$LOG_FILE${NC}"
    else
        echo -e "\n${RED}╔════ FAILED ════╗${NC}"
        echo -e "${RED}║${NC} Installation encountered errors"
        echo -e "${RED}╚═══════════════╝${NC}"
        
        echo -e "\n${YELLOW}Last few lines of log:${NC}"
        echo "----------------------------------------"
        tail -n 10 "$LOG_FILE" | grep -v "password for" | while read -r line; do
            echo "  $line"
        done
        echo "----------------------------------------"
        
        if [[ "$USE_GUI" == "true" ]]; then
            whiptail --title "Installation Failed" --msgbox "Installation failed.\n\nPlease check the logs at: $LOG_FILE" $MSG_HEIGHT $WHIP_COLS
        fi
        
        echo -e "\nFull logs available at: ${BOLD}$LOG_FILE${NC}"
        exit 1
    fi
}
