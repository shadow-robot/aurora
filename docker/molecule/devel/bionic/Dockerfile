FROM shadowrobot/aurora-molecule-docker:bionic

MAINTAINER "Shadow Robot's Software Team <software@shadowrobot.com>"

LABEL Description="Ubuntu Bionic image contains Ansible, Molecule, Docker and EC2 driver and Development tools with GUI" Vendor="Shadow Robot" Version="1.0"

ENV DEBIAN_FRONTEND noninteractive

ENV PULSE_SERVER /run/pulse/native

ARG aurora_branch

ENV aurora_branch ${aurora_branch:-"master"}

ENV aurora_script "https://raw.githubusercontent.com/shadow-robot/aurora/$aurora_branch/bin/run-ansible.sh"

RUN set -x && \
    \
    echo "Downloading one-liner" && \
    wget -O /tmp/oneliner "$( echo "$aurora_script" | sed 's/#/%23/g' )" && \
    chmod 755 /tmp/oneliner && \
    \
    echo "Setting up UI and new Docker user" && \
    /tmp/oneliner configure-software --debug-branch $aurora_branch software=[setup-docker] && \
    \
    echo "Add user to docker group" && \
    usermod -aG docker user && \
    \
    echo "Installing IDEs and AWS CLI" && \
    /tmp/oneliner install-software --debug-branch $aurora_branch software=[pycharm,vscode,aws-cli] && \
    \
    echo "Clean up" && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /root/.ansible /root/.gitconfig /root/.cache

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

CMD ["/usr/bin/terminator"]
