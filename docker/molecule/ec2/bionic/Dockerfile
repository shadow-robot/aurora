FROM shadowrobot/aurora-molecule:bionic

MAINTAINER "Shadow Robot's Software Team <software@shadowrobot.com>"

LABEL Description="Ubuntu Bionic image contains Ansible, Molecule and EC2 driver" Vendor="Shadow Robot" Version="1.0"

ARG branch="master"

ENV aurora_branch=$branch

ENV aurora_script "https://raw.githubusercontent.com/shadow-robot/aurora/$aurora_branch/bin/run-ansible.sh"

RUN set -x && \
    \
    echo "Installing AWS CLI" && \
    wget -O /tmp/oneliner "$( echo "$aurora_script" | sed 's/#/%23/g' )" && \
    chmod 755 /tmp/oneliner && \
    /tmp/oneliner install_software --debug-branch $aurora_branch software=[aws-cli] && \
    \
    echo "Clean up" && \
    apt-get clean && \
    rm -rf \
        /var/lib/apt/lists/* \
        /tmp/* \
        /var/tmp/* \
        /root/.ansible \
        /root/.gitconfig \
        /root/.cache
