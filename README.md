# Table of Contents
- [Introduction](#introduction)
- [Development](#development)
  * [Development Docker](#development-docker)
- [Testing](#testing)
  * [Testing with molecule_docker](#testing-with-molecule_docker)
  * [Private docker images](#private-docker-images)
  * [Testing with molecule_ec2](#testing-with-molecule_ec2)
  * [Credentials](#credentials)
  * [Automatic tests](#automatic-tests)
  * [Test creation](#test-creation)
  * [Testing on real hardware](#testing-on-real-hardware)
  * [Ethercat interface](#ethercat-interface)
- [Deployment](#deployment)
- [Structure of files](#structure-of-files)
  * [Roles](#roles)
  * [Docker](#docker)
  * [Installation](#installation)
  * [Products](#products)
  * [Common](#common)
  * [Dependencies](#dependencies)
- [Playbooks and possible command line arguments](#playbooks-and-possible-command-line-arguments)
  * [Playbook creation](#playbook-creation)
  * [teleop_deploy](#teleop_deploy)
  * [docker_deploy](#docker_deploy)
  * [configure_software](#configure_software)
  * [install_software](#install_software)
  * [install_python3](#install_python3)
- [Inventories](#inventories)
- [Molecule tests](#molecule-tests)
  * [Docker tests](#docker-tests)
  * [AWS EC2 tests](#aws-ec2-tests)
- [Syntax and rules](#syntax-and-rules)
- [Tutorial 1: desktop icon](#tutorial-1:-desktop-icon)

# Introduction #

Aurora is an installation automation tool using Ansible. It uses Molecule for testing Ansible scripts and it has automated builds in AWS EC2/CodeBuild and DockerHub. It can be used to develop, test and deploy complicated, multi-machine, multi-operating-system automated installs of software. Aurora's purpose is to unify one-liners approaches based on Ansible best practices.

For example, it's possible to use Aurora to install Docker, download the specified image and create a new container for you. It will also create a desktop icon to start the container and launch the hand.

Ansible user guide is available [here](https://docs.ansible.com/ansible/latest/user_guide/index.html) (Aurora is currently using Ansible 2.8.1)

Molecule user guide is available [here](https://molecule.readthedocs.io/en/stable/) (Aurora is currently using Molecule 2.20.1)

# Development #

The recommended way to develop code for this project is to pull a certain docker image ([Development Docker](#development-docker)) with a lot of tools already installed and open a container of this image, then clone the aurora GitHub repository inside it. It is not recommended to clone aurora directly on your local machine while you do development and testing.

## Development Docker ##

The docker images used for aurora development are [here](https://cloud.docker.com/u/shadowrobot/repository/docker/shadowrobot/aurora-molecule-devel)

Currently both xenial and bionic tags are working well and there is no difference.
The rest of the document assumes the user is using bionic tag.

Instructions on how to use this:
1. Use Ubuntu 16.04 or Ubuntu 18.04 computer

2. Install Docker (using instructions from [here](https://docs.docker.com/install/linux/docker-ce/ubuntu/))

3. Run the following command in terminal to create a container for aurora development:

```
docker run -it --name aurora_dev -e DISPLAY -e QT_X11_NO_MITSHM=1 -e LOCAL_USER_ID=$(id -u) -v /var/run/docker.sock:/var/run/docker.sock -v /tmp/.X11-unix:/tmp/.X11-unix:rw shadowrobot/aurora-molecule-devel:bionic
```
4. Once the container has launched, clone aurora to it:
```
git clone https://github.com/shadow-robot/aurora.git
```
5. Go into the aurora folder:
```
cd aurora
```
6. Open Visual Studio Code which is already installed inside the Docker container:
```
code
```
7. Open the aurora folder in Visual Studio Code

# Testing #

## Testing with molecule_docker ##

Once you have written your code for aurora in your branch, test it locally with Molecule first before pushing to GitHub.

1. In the docker container terminal go to /ansible/playbooks/molecule_docker folder

```
cd /home/user/aurora/ansible/playbooks/molecule_docker
```

2. Run the following command to execute all molecule tests locally with debug mode:

```
molecule --debug test --all
```

3. Fix any errors

4. If you want to run a specific test case (scenarios are in ansible/playbooks/molecule_docker/molecule folder), use:

```
molecule --debug test -s name_of_your_scenario
```
5. Often it is useful to run molecule in stages (create, converge, verify, login (if necessary), and finally destory) for better debugging (so you can inspect every stage yourself). See [this](https://molecule.readthedocs.io/en/stable/usage.html) page, and do, for example:
```
molecule --debug create -s name_of_your_scenario
molecule --debug converge -s name_of_your_scenario
molecule --debug verify -s name_of_your_scenario
molecule --degub login -s name_of_your_scenario
molecule --debug destroy -s name_of_your_scenario
```
## Private docker images ##

At the moment, we don't want to give molecule access to private docker hub credentials for private docker images (e.g. shadow-teleop). That is why, in every playbook.yml inside the test scenarios in the molecule_docker folder, we override the image with image="shadowrobot/dexterous-hand" for any teleop-related test scenario. When we actually deploy Aurora, the user will be asked to fill in their private Docker hub credentials.

## Testing with molecule_ec2 ##

Once you have written your code for aurora in your branch, and tested it locally with molecule_docker, you can test it with AWS EC2 (initiated from local), by following the steps here:

## Credentials ##

1. Ask the system adminstrator for your AWS access key and secret access key. Then, in the docker container terminal, type:

```
aws configure
```
2. Paste the access key and the secret access key

3. Default region name must be: eu-west-2

4. Press enter on the Default format


Then continue testing with molecule_ec2:

1. In the docker container terminal go to /ansible/playbooks/molecule_ec2 folder

```
cd /home/user/aurora/ansible/playbooks/molecule_ec2
```

2. Run the following command to execute all AWS EC2 molecule tests in AWS (but you can see local debug logs):

```
molecule --debug test --all
```

3. Fix any errors

4. If you want to run a specific test case (the AWS EC2 scenarios are in ansible/playbooks/molecule_ec2/molecule folder), use:

```
molecule --debug test -s name_of_your_scenario
```
5. Often it is useful to run molecule in stages (create, converge, verify, login (if necessary), and finally destory) for better debugging (so you can inspect every stage yourself). See [this](https://molecule.readthedocs.io/en/stable/usage.html) page, and do, for example:
```
molecule --debug create -s name_of_your_scenario
molecule --debug converge -s name_of_your_scenario
molecule --debug verify -s name_of_your_scenario
molecule --degub login -s name_of_your_scenario
molecule --debug destroy -s name_of_your_scenario
```
## Automatic tests ##

The buildspec.yml file in the root of the project defines what AWS CodeBuild should run when a PR is created or updated or when a daily build runs. It is configured to run all tests in /ansible/playbooks/molecule_ec2 folder

## Test creation ##

Create test scenarios for both docker in ansible/playbooks/molecule_docker/molecule folder and for AWS EC2 in ansible/playbooks/molecule_ec2/molecule folder. For additional molecule_docker tests, copy the folder structure from other tests and modify the python .py file in tests folder.For additional molecule_ec2 tests, copy the folder structure of another EC2 test and modify the molecule.yml file inside. The EC2 tests just run the same tests as the Docker tests, but they do it in AWS EC2, using virtual machines, not Docker.

## Testing or deploying on real hardware ##

For debugging (not using the master branch), you can add the following immediately after playbook name (for example docker_deploy or teleop_deploy):

* --debug-branch name_of_aurora_repo_branch (e.g. --debug-branch F#SRC-2603_add_ansible_bootstrap)

Run a playbook against one or more members of that group using the --limit tag:

* --limit rules (e.g. --limit 'all:!server' please use single quotes. More details could be found 
[here](https://ansible-tips-and-tricks.readthedocs.io/en/latest/ansible/commands/#limit-to-one-or-more-hosts))

For assigning input and secure input to playbook variables you can use the tags: --read-input var1, var2, var3 ... and --read-secure secure_var1, secure_var2, secure_var3 ... respectively

* --read-input vars (e.g. --read-input docker_username - To allow aurora script to prompt for docker username)
* --read-secure secure_vars (e.g. --read_secure docker_password - To allow aurora script to prompt for docker password)

## Ethercat interface ##

Before running the docker_deploy playbook ##

Before setting up the docker container, ethercat_interface parameter for the hand needs to be discovered. In order to do so, after plugging the hand’s ethernet cable into your machine and powering it up, please run
```shell
sudo dmesg
```
command in the console. At the bottom, there will be information similar to the one below:
```shell
[490.757853] IPv6: ADDRCONF(NETDEV_CHANGE): enp0s25: link becomes ready
```
In the above example, ‘enp0s25’ is the ethercat_interface that is needed.

# Deployment #

# Structure of files #

# Roles #

Everything you need to do in Ansible is achieved using roles. Roles basically mean: "execute this set of tasks" (defined in the role's tasks/main.yml file). The roles folder is very important and contains roles and tasks for teleop, hand_e, hand_h and a common role section. It is very important that you re-use existing roles whenever possible to avoid code duplication. Please read about roles [here](https://docs.ansible.com/ansible/latest/user_guide/playbooks_reuse_roles.html) 

The roles folder contains the following sub-folders:

[Docker](#docker)

[Installation](#installation)

[Products](#products)


## Docker ##

The docker folder contains some general roles that are used in after docker install. It has the following folders:

aws: this is used for installing our shadow-upload.sh script and AWS customer key which uploads ROS logs to AWS. It has a dependency of installation/aws-cli

docker-image: this is used for pulling the docker image (and if nvidia_docker it not 0, it will append -nvidia to the docker image before it is pulled)

setup-ui: this is used to install various UI libraries, terminator, vim, git, subversion, bash-completion, and to create the /usr/local/bin/entrypoint.sh file

## Installation ##

Any programs that need to be installed are placed in the installation role. It has the following folders:

aws-cli
chrony-client
chrony-server
docker
nvidia-docker
openvpn-client
openvpn-server
pycharm
qtcreator
steamvr
vscode

## Products ##

The Products folder (/ansible/roles/products) contains groupings of roles under folders:

common
hand-e
hand-h
teleop

The logic is: everything to do with hand-e is in the hand-e folder, everything to do with teleop is in the teleop folder.
The common product is special, see below.

## Common ##

The common role contains any common task or roles that is used repeatedly in many different products. 

It contains the following roles:

cyberglove
demo-icons
docker-container
resources
save-logs-icons

For example, since docker-container contains the Ansible scripts for creating a Docker container, and it is a very common task shared by many products, it makes sense to have it in common so it can be referred to by other products.

Whenever you create a role, if it will likely be used by other products (e.g. it's not very specific to your product), please put it under common roles, or if it's for installing some commonly used program, put it under installation.

## Dependencies ##

There are 2 main way of including dependencies in Ansible roles. The primary way we use is the "include_role" method because it is dynamic (see [here](https://docs.ansible.com/ansible/latest/modules/include_role_module.html) for documentation).

E.g. if we want to include a particular role to install Docker, we do:

```bash
- name: Include installation/docker role
  include_role:
    name: installation/docker
```
The other way of having dependencies in Ansible is by using the meta folder and main.yml inside the meta folder. Any tasks in meta/main.yml are run before the task/main.yml. An example of meta/main.yml:

```bash
dependencies:
  - { role: installation/aws-cli }
```

# Playbooks and possible command line arguments #

## Playbook creation ##

Create your playbook in ansible/playbooks folder. It has be a .yml file with no hyphens (underscores are allowed).

You can read more about playbooks [here](https://docs.ansible.com/ansible/latest/user_guide/playbooks_intro.html)

It has to have a similar structure to this:

```bash
---

- name: Install Python 3
  import_playbook: ./install_python3.yml

- name: Install product Docker container and icons
  hosts: docker_deploy
  pre_tasks:

    - name: No product is defined
      when: product != 'hand_e' and product != 'hand_h'
      meta: end_play

    - name: check if customer_key is provided and not false
      when: customer_key is defined and customer_key|bool
      set_fact:
        use_aws: true

    - name: check if cyberglove branch is provided
      when: cyberglove is defined and cyberglove|bool
      set_fact:
        use_cyberglove: true

  roles:
    - {role: installation/docker}
    - {role: installation/nvidia-docker, when: nvidia_docker | int != 0}
    - {role: products/hand-h/deploy, when: product == 'hand_h'}
    - {role: products/hand-e/deploy, when: product == 'hand_e'}
    - {role: docker/aws, when: use_aws|bool}
```
Key points:

Always start by having:

```bash
- name: Install Python 3
  import_playbook: ./install_python3.yml
```
This is to ensure Python3 is installed. Aurora uses Python3.

Then you need to have one or more of task sections (or pre-task sections, which are executed before tasks) and an optional role section. Another example of a task section in a playbook (without role section):

```bash
- name: Check which hosts are available for teleop system Install
  hosts: all
  gather_facts: no
  tasks:
    - name: ping all the machines
      ping:
  become: yes
```
Some task sections specify "hosts", which tells Ansible which hosts to limit the execution to. You can read more about hosts in playbooks [here](https://docs.ansible.com/ansible/latest/user_guide/playbooks_intro.html#hosts-and-users)

An example of a role section:

```bash
  roles:
    - {role: installation/docker}
    - {role: installation/nvidia-docker, when: nvidia_docker | int != 0}
    - {role: products/hand-h/deploy, when: product == 'hand_h'}
    - {role: products/hand-e/deploy, when: product == 'hand_e'}
    - {role: docker/aws, when: use_aws|bool}
```

## teleop_deploy ##

For deploying teleop software on multiple machines (server, control-machine, client, windows-machine)

How to run:

Open a terminal with Ctrl+Alt+T and run:

```bash
bash <(curl -Ls bit.ly/run-aurora) teleop_deploy --inventory name_of_inventory option1=value1 option2=value2 option3=value3
```
name_of_inventory can be development, staging or production. If you are not sure which to use, use staging.

Inventories correspond to fixed IP addresses as shown here:
* [development](ansible/inventory/teleop/development)
* [staging](ansible/inventory/teleop/staging)
* [production](ansible/inventory/teleop/production)

Options for teleop_deploy playbook are here for the following machines:
* [server](ansible/inventory/teleop/group_vars/server.yml)
* [control-machine](ansible/inventory/teleop/group_vars/control-machine.yml)
* [client](ansible/inventory/teleop/group_vars/client.yml)
* [windows-machine](ansible/inventory/teleop/group_vars/windows-machine.yml)

## docker_deploy ##

For Hand E/G/H software deployments on single laptop.

To begin with, the docker_deploy playbook checks the installation status of docker. If docker is not installed then a 
new clean installation is performed. If the required image is private, 
then a valid Docker Hub account with pull credentials from Shadow Robot's Docker Hub is required. Then the specified docker image is pulled and a docker 
container is initialized. Finally, a desktop shortcut is generated. This shortcut starts the docker container and 
launches the hand.

How to run:

Open a terminal with Ctrl+Alt+T and run:

```bash
bash <(curl -Ls bit.ly/run-aurora) docker_deploy option1=value1 option2=value2 option3=value3
```

Example:

```bash
bash <(curl -Ls bit.ly/run-aurora) docker_deploy product=hand_e ethercat_interface=enp0s25
```

Options for docker_deploy playbook are [here](ansible/inventory/local/group_vars/docker_deploy.yml)

## configure_software ##

## install_software ##

## install_python3 ##

# Inventories #



# Molecule tests #

## Docker tests ##
## AWS EC2 tests ##

# Syntax and rules #

# Tutorial 1: desktop icon #

Aim: to create a branch of aurora which has an Ansible role to install a desktop icon. When the user clicks on the desktop icon, a terminal window will open and say: "Hello, User!". The user can supply a different username as an extra vars parameter, so e.g. if the user runs the playbook with username=Peter, the terminal window will show "Hello, Peter!"

Requirements: you need a laptop/PC with internet, Ubuntu 16.04 or 18.04 installed.

Steps:

1. Create your own branch of aurora (from master). You can call your branch: Tutorial_YourName

2. Go to [Development Docker](#development-docker) section and follow instructions there to set up your development environment

3. Follow instructions in the [Playbook creation](#playbook-creation) section to create your own playbook, you can call it tutorial_icon_deploy.yml. Remember use the Install Python3 import as documented in [Playbook creation](#playbook-creation) and include a roles section. Your playbook should look something like this (yes, use hosts: docker_deploy for this tutorial):

```bash
---

- name: Install Python 3
  import_playbook: ./install_python3.yml

- name: TODO
  hosts: docker_deploy
  roles:
    - {role: TODO}
```

4. Create a role for in roles/products/tutorial folder (you will have to create the tutorial folder). Inside the tutorial folder, create sub-folders deploy and desktop-icons. Inside deploy and desktop-icons folders, create sub-folders defaults and tasks, in each folder. Inside those, create an empty main.yml file. Also create a sub-folder files inside desktop-icons folder. You should have the following file structure:

products
   (some other folders)
   tutorial
      deploy
         defaults
            main.yml
         tasks
            main.yml
      desktop-icons
         defaults
            main.yml
         tasks
            main.yml
         files

5. Edit your playbook's (tutorial_icon_deploy.yml) role section to point to the tutorial role's deploy section like this:

```bash
  roles:
    - {role: products/tutorial/deploy}
```
6. deploy/defaults/main.yml
Your main.yml file here should look like this:
```bash
---
user: "{{ ansible_user_id }}"
user_folder: "/home/{{ user }}"
```





