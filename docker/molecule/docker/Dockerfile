FROM shadowrobot/aurora-molecule:xenial

MAINTAINER "Shadow Robot's Software Team <software@shadowrobot.com>"

LABEL Description="This image contains Ansible, Molecule and Docker driver" Vendor="Shadow Robot" Version="1.0"

ENV aurora_branch="F#SRC-3066_adding_molecule"
#ENV aurora_branch="master"

ENV remote_shell_script="https://raw.githubusercontent.com/shadow-robot/aurora/$aurora_branch/bin/run-ansible.sh"

RUN set -x && \
    apt-get update && \
    \
    echo "Install sudo and sshpass" && \
    apt install -y sudo sshpass && \
    \
    echo "Install Docker using playbook to avoid installing Python 3.5" && \
    git clone --depth 1 https://github.com/shadow-robot/aurora.git -b $aurora_branch /tmp/aurora && \
    cd /tmp/aurora/ && \
    export ANSIBLE_ROLES_PATH="/tmp/aurora/ansible/roles" && \
    ansible-playbook -vvv --ask-become-pass -i ansible/inventory/local ansible/playbooks/install-software.yml \
        --extra-vars 'software=[docker]' && \
    \
    echo "Clean up" && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /root/.ansible /root/.gitconfig /root/.cache
