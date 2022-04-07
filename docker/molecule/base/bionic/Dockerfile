FROM public.ecr.aws/shadowrobot/ubuntu:bionic

LABEL Description="This Ubuntu Bionic image contains Ansible and Molecule" Vendor="Shadow Robot" Version="1.0.0"

ENV DEBIAN_FRONTEND noninteractive

ENV LC_ALL C.UTF-8

ENV LANG C.UTF-8

ARG ml_base_aurora_branch

ENV ml_base_aurora_branch ${ml_base_aurora_branch:-"SP-196_update_ansible_reqs"}

RUN set -x && \
    apt-get update && \
    \
    echo "Installing git, sudo and Python 3" && \
    apt-get install -y \
         python3-dev \
         python3-pip \
         git \
         libyaml-dev \
         python-crypto \
         libssl-dev \
         libffi-dev \
         sshpass \
         sudo && \
    \
    echo "Installing wget" && \
    apt-get install -y --no-install-recommends ca-certificates wget && \
    \
    echo "Cloning Aurora" && \
    git clone --depth 1 https://github.com/shadow-robot/aurora.git -b $ml_base_aurora_branch /tmp/aurora && \
    \
    echo "Installing molecule" && \
    pip3 install -r /tmp/aurora/ansible/data/molecule/bionic/requirements.txt && \
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

VOLUME /var/lib/docker
