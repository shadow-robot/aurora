FROM ubuntu:xenial-20201030

MAINTAINER "Shadow Robot's Software Team <software@shadowrobot.com>"

LABEL Description="Ubuntu Xenial image contains Ansible and Molecule" Vendor="Shadow Robot" Version="1.0"

ENV DEBIAN_FRONTEND noninteractive

ENV LC_ALL C.UTF-8

ENV LANG C.UTF-8

ARG ml_base_aurora_branch

ENV ml_base_aurora_branch ${ml_base_aurora_branch:-"master"}

RUN set -x && \
    apt-get update && \
    \
    echo "Installing wget" && \
    apt-get install -y --no-install-recommends ca-certificates wget && \
    \
    echo "Installing python 3.6 as required by Molecule" && \
    cd /opt && \
    wget https://www.python.org/ftp/python/3.6.9/Python-3.6.9.tgz && \
    tar -xvf Python-3.6.9.tgz && \
    cd Python-3.6.9 && \
    echo "Installing dependencies for python3.6, SSL, pip3" && \
    apt-get install -y build-essential zlib1g-dev libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev && \
    ./configure && \
    make && \
    make install && \
    update-alternatives --install /usr/bin/python3 python3 /opt/Python-3.6.9/python 1 && \
    python3 --version && \
    \
    echo "Installing git, sudo and Python 3 pip and dev" && \
    apt-get install -y \
         python3-pip \
         git \
         libyaml-dev \
         python-crypto \
         libssl-dev \
         libffi-dev \
         sshpass \
         sudo \
         python3-dev && \
    \
    echo "Cloning Aurora" && \
    git clone --depth 1 https://github.com/shadow-robot/aurora.git -b $ml_base_aurora_branch /tmp/aurora && \
    \
    echo "Installing molecule" && \
    pip3 install -r /tmp/aurora/ansible/data/molecule/requirements.txt && \
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
