FROM ubuntu:xenial-20190222

#ENV aurora_branch="master"
ENV aurora_branch="F#SRC-3066_adding_molecule"

RUN set -x && \
    apt-get update && \
    \
    echo "Installing git" && \
    apt-get install -y git && \
    \
    echo "Installing wget" && \
    apt-get install -y --no-install-recommends ca-certificates wget && \
    \
    echo "Installing Python 3.7 for Ubuntu Xenial from source code" && \
    mkdir -p /tmp/python && \
    wget -c https://www.python.org/ftp/python/3.7.0/Python-3.7.0.tar.xz && \
    tar xf Python-3.7.0.tar.xz && \
    cd /tmp/python/Python-3.7.0 && \
    ./configure && \
    make && \
    make install && \
    \
    echo "Installing Pip for Python 3.7" && \
    cd /tmp && \
    wget "https://bootstrap.pypa.io/get-pip.py" && \
    python3.7 ./get-pip.py && \
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
    echo "Clonning Aurora" && \
    cd /tmp && \
    git clone --depth 1 https://github.com/shadow-robot/aurora.git -b $aurora_branch && \
    \
    echo "Installing molecule" && \
    pip3.7 install -r /tmp/aurora/ansible/data/molecule/requirements.txt && \
    \
    echo "Clean up" && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /root/.ansible /root/.gitconfig /root/.cache
