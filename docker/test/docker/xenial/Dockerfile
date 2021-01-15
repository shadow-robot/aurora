FROM shadowrobot/aurora-test-ubuntu:xenial

MAINTAINER "Shadow Robot's Software Team <software@shadowrobot.com>"

LABEL Description="This image is used for testing Ubuntu Xenial with Docker deployment" Vendor="Shadow Robot" Version="1.0"

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
    echo "Installing python 3.6 as required by latest Ansible" && \
    cd /opt && \
    sudo wget https://www.python.org/ftp/python/3.6.9/Python-3.6.9.tgz && \
    sudo tar -xvf Python-3.6.9.tgz && \
    cd Python-3.6.9 && \
    echo "Installing dependencies for python3.6, SSL, pip3" && \
    sudo apt-get install -y build-essential zlib1g-dev libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev && \
    sudo ./configure && \
    sudo make && \
    sudo make install && \
    sudo update-alternatives --install /usr/bin/python3 python3 /opt/Python-3.6.9/python 1 && \
    python3 --version && \
    \
    echo "Installing git, sudo and Python 3 pip and dev" && \
    sudo apt-get install -y \
         python3-pip \
         git \
         libyaml-dev \
         python-crypto \
         libssl-dev \
         libffi-dev \
         sshpass \
         python3-dev && \
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
