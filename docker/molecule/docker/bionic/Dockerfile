FROM public.ecr.aws/shadowrobot/aurora-molecule:bionic

LABEL Description="Ubuntu Bionic image contains Ansible, Molecule and Docker driver" Vendor="Shadow Robot" Version="1.0"

# ARG ml_docker_aurora_branch

ENV LC_ALL C.UTF-8

ENV LANG C.UTF-8

ENV ml_docker_aurora_branch "F_testing_conda_deployment"

ENV ml_docker_aurora_script "https://raw.githubusercontent.com/shadow-robot/aurora/F_testing_conda_deployment/bin/run-ansible.sh"

RUN set -x && \
    \
    echo "Installing Docker" && \
    wget -O /tmp/oneliner "$( echo "$ml_docker_aurora_script" | sed 's/#/%23/g' )" && \
    chmod 755 /tmp/oneliner && \
    /tmp/oneliner install_software --branch $ml_docker_aurora_branch software=[docker] skip_molecule_task=true && \
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
