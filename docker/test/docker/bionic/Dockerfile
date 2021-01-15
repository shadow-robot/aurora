FROM shadowrobot/aurora-test-ubuntu:bionic

MAINTAINER "Shadow Robot's Software Team <software@shadowrobot.com>"

LABEL Description="This image is used for testing Ubuntu Bionic with Docker deployment" Vendor="Shadow Robot" Version="1.0"

ENV DEBIAN_FRONTEND noninteractive

ENV USER testuser

ARG ts_docker_aurora_branch

ENV ts_docker_aurora_branch ${ts_docker_aurora_branch:-"master"}

ENV ts_docker_aurora_script "https://raw.githubusercontent.com/shadow-robot/aurora/$ts_docker_aurora_branch/bin/run-ansible.sh"

RUN set -x && \
    sudo apt-get update && \
    \
    echo "Installing wget" && \
    sudo apt-get install -y --no-install-recommends ca-certificates wget && \
    \
    echo "Installing Docker" && \
    wget -O /tmp/oneliner "$( echo "$ts_docker_aurora_script" | sed 's/#/%23/g' )" && \
    chmod 755 /tmp/oneliner && \
    /tmp/oneliner install_software --branch $ts_docker_aurora_branch software=[docker] && \
    \
    echo "Clean up" && \
    sudo apt-get clean && \
    sudo rm -rf \
        /var/lib/apt/lists/* \
        /tmp/* \
        /var/tmp/* \
        /root/.ansible \
        /root/.gitconfig \
        /root/.cache
