FROM ubuntu:bionic-20190307

MAINTAINER "Shadow Robot's Software Team <software@shadowrobot.com>"

LABEL Description="This Ubuntu Bionic image contains Ansible and Molecule" Vendor="Shadow Robot" Version="1.0"

ENV DEBIAN_FRONTEND noninteractive

ENV aurora_branch "F#SRC-3068_add_docker_for_testing"

RUN set -x && \
    apt-get update && \
    \
    echo "Installing git and Python 3" && \
    apt-get install -y \
         python3-pip \
         git \
         libyaml-dev \
         python-crypto \
         libssl-dev \
         libffi-dev \
         sshpass && \
    \
    echo "Clonning Aurora" && \
    git clone --depth 1 https://github.com/shadow-robot/aurora.git -b $aurora_branch /tmp/aurora && \
    \
    echo "Installing molecule" && \
    pip3 install -r /tmp/aurora/ansible/data/molecule/requirements.txt && \
    \
    echo "Clean up" && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /root/.ansible /root/.gitconfig /root/.cache
