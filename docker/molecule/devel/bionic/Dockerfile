FROM shadowrobot/aurora-molecule-docker:bionic

MAINTAINER "Shadow Robot's Software Team <software@shadowrobot.com>"

LABEL Description="Ubuntu Bionic image contains Ansible, Molecule, Docker driver and Development tools with GUI" Vendor="Shadow Robot" Version="1.0"

ENV DEBIAN_FRONTEND noninteractive

ENV PULSE_SERVER /run/pulse/native

ENV aurora_branch "F#SRC-3068_add_docker_for_testing"

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
    echo "Installing IDEs" && \
    /tmp/oneliner install-software --debug-branch $aurora_branch software=[pycharm,vscode] && \
    \
    echo "Clean up" && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /root/.ansible /root/.gitconfig /root/.cache

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

CMD ["/usr/bin/terminator"]
