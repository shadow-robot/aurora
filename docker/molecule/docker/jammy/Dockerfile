FROM public.ecr.aws/shadowrobot/aurora-molecule:jammy

LABEL Description="Ubuntu Jammy image contains Ansible, Molecule and Docker driver" Vendor="Shadow Robot" Version="1.0"

ARG ml_docker_aurora_branch

ENV ml_docker_aurora_branch ${ml_docker_aurora_branch:-"master"}

ENV ml_docker_aurora_script "https://raw.githubusercontent.com/shadow-robot/aurora/$ml_docker_aurora_branch/bin/run-ansible.sh"

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
