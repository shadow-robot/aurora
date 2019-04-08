FROM aurora-ubuntu-frozen:xenial

RUN set -x && \
    apt-get update && \
    \
    echo "Install Docker" && \
    apt-get install \
        apt-transport-https \
        ca-certificates \
        curl \
        gnupg-agent \
        software-properties-common && \
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add - && \
    apt-key fingerprint 0EBFCD88 && \
    add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu xenial stable" && \
    apt-get update && \
    apt-get install docker-ce docker-ce-cli containerd.io && \
    \
    echo "Installing git" && \
    apt-get install -y git && \
    \
    echo "Installing pip 3" && \

# clone aurora

# install molecule

