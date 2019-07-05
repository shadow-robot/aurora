## Table of Contents  
- [Development](#development)
  * [Development Docker](#development-docker)
- [Testing](#testing)
  * [Testing with molecule_docker](#testing-with-molecule_docker)
  * [Testing with molecule_ec2](#testing-with-molecule_ec2)
  * [Automatic tests](#automatic-tests)
  * [Test creation](#test-creation)
  * [Testing on real hardware](#testing-on-real-hardware)
  * [Ethercat interface](#ethercat-interface)
- [Deployment](#deployment)
- [Structure of files](#structure-of-files)
  * [Common](#common)
  * [Products](#products)
  * [Dependencies](#dependencies)
- [Playbooks and possible command line arguments](#playbooks-and-possible-command-line-arguments)
  * [Playbook creation](#playbook-creation)
  * [teleop_deploy](#teleop_deploy)
  * [docker_deploy](#docker_deploy)
  * [configure_software](#configure_software)
  * [install_software](#install_software)
  * [install_python3](#install_python3)
- [Inventories](#inventories)
- [Roles](#roles)
- [Molecule tests](#molecule-tests)
  * [Docker tests](#docker-tests)
  * [AWS EC2 tests](#aws-ec2-tests)
- [Syntax and rules](#syntax-and-rules)

# Aurora project #

Aurora is an installation automation tool using Ansible. It uses Molecule for testing Ansible scripts and it has automated builds in AWS EC2/CodeBuild and DockerHub. It can be used to develop, test and deploy complicated, multi-machine, multi-operating-system automated installs of software. Aurora's purpose is to unify one-liners approaches based on Ansible best practices.

For example, it's possible to use Aurora to install Docker, download the specified image and create a new container for you. It will also create a desktop icon to start the container and launch the hand.

Ansible user guide is available [here](https://docs.ansible.com/ansible/latest/user_guide/index.html) (We are currently using Ansible 2.8.1)

Molecule user guide is available [here](https://molecule.readthedocs.io/en/stable/) (We are currently using Molecule 2.20.1)

For certain tests (e.g. AWS EC2 tests) and certain private docker images, contact the system administrator to ask for access

## Development ##

The preferred way to develop code for this project is to pull a certain docker image with a lot of tools already installed and open a container in it, then clone the aurora GitHub repository inside it. It is not recommended to clone aurora directly on your local machine while you do development and testing.

Instructions how to access the docker image and container for development, see Development Docker section below

### Development Docker ###

The docker images used for aurora development are [here](https://cloud.docker.com/u/shadowrobot/repository/docker/shadowrobot/aurora-molecule-devel)

Currently both xenial and bionic tags are working well and there is no difference.
The rest of the document assumes the user is using bionic tag.

Instructions on how to use this:
1. Use a Ubuntu 16.04 or Ubuntu 18.04 computer
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


## Testing ##

### Testing with molecule_docker ###

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
5. If you want to to run Molecule in stages (create, converge, etc.), see [this](https://molecule.readthedocs.io/en/stable/usage.html) page, and do, for example:
```
molecule --debug create -s name_of_your_scenario
molecule --debug converge -s name_of_your_scenario
molecule --debug test -s name_of_your_scenario
molecule --debug destroy -s name_of_your_scenario
```
### Testing with molecule_ec2 ###

Once you have written your code for aurora in your branch, and tested it locally with molecule_docker, you can test it with AWS EC2 (initiated from local), by following the steps here:

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
5. If you want to to run Molecule in stages (create, converge, etc.), see [this](https://molecule.readthedocs.io/en/stable/usage.html) page, and do, for example:
```
molecule --debug create -s name_of_your_scenario
molecule --debug converge -s name_of_your_scenario
molecule --debug test -s name_of_your_scenario
molecule --debug destroy -s name_of_your_scenario
```
### Automatic tests ###

The buildspec.yml file in the root of the project defines what AWS CodeBuild should run when a PR is created or updated or when a daily build runs. It is configured to run all tests in /ansible/playbooks/molecule_ec2 folder

### Test creation ###

Create test scenarios for both docker in ansible/playbooks/molecule_docker/molecule folder and for AWS EC2 in ansible/playbooks/molecule_ec2/molecule folder. Copy the folder structure from other tests and modify the python .py file in tests folder.

### Testing or deploying on real hardware ###

For debugging (not using the master branch), you can add the following immediately after playbook name (for example docker_deploy or teleop_deploy):

* --debug-branch name_of_aurora_repo_branch (e.g. --debug-branch F#SRC-2603_add_ansible_bootstrap)

Run a playbook against one or more members of that group using the --limit tag:

* --limit rules (e.g. --limit 'all:!server' please use single quotes. More details could be found 
[here](https://ansible-tips-and-tricks.readthedocs.io/en/latest/ansible/commands/#limit-to-one-or-more-hosts))

For assigning input and secure input to playbook variables you can use the tags: --read-input var1, var2, var3 ... and --read-secure secure_var1, secure_var2, secure_var3 ... respectively

* --read-input vars (e.g. --read-input docker_username - To allow aurora script to prompt for docker username)
* --read-secure secure_vars (e.g. --read_secure docker_password - To allow aurora script to prompt for docker password)

#### Ethercat interface ####

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

## Structure of files ##

### Common ###

### Products ###

### Dependencies ###

## Playbooks and possible command line arguments ##

### Playbook creation ###

### teleop_deploy ###

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

### docker_deploy ###

For Hand E/G/H software deployments on single laptop.

To begin with, the docker_deploy playbook checks the installation status of docker. If docker is not installed then a 
new clean installation is performed. If the required image is private, 
then a valid Docker Hub account with pull credentials from Shadow Robot's Docker Hub is required. Then, 
the specified docker image is pulled and a docker 
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

### configure_software ###

### install_software ###

### install_python3 ###

## Inventories ##

## Roles ##

## Molecule tests ##

### Docker tests ###

### AWS EC2 tests ###

## Syntax and rules ##
