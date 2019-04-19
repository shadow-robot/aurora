FROM shadowrobot/aurora-molecule:bionic

MAINTAINER "Shadow Robot's Software Team <software@shadowrobot.com>"

LABEL Description="This image contains Ansible, Molecule and Docker driver" Vendor="Shadow Robot" Version="1.0"

ENV aurora_branch "F#SRC-3068_add_docker_for_testing"

ENV aurora_script "https://raw.githubusercontent.com/shadow-robot/aurora/$aurora_branch/bin/run-ansible.sh"

RUN set -x && \
    apt update && \
    \
    echo "Installing wget" && \
    apt install -y --no-install-recommends ca-certificates wget && \
    \
    echo "Installing Docker" && \
    wget -O /tmp/oneliner "$( echo "$aurora_script" | sed 's/#/%23/g' )" && \
    chmod 755 /tmp/oneliner && \
    /tmp/oneliner install-software --debug-branch $aurora_branch software=[docker] && \
    \
    echo "Clean up" && \
    apt clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /root/.ansible /root/.gitconfig /root/.cache
