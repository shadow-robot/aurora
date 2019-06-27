##### Table of Contents  
[Development](#development)  
[Emphasis](#emphasis)

# Aurora project #

Aurora is an installation automation tool using Ansible. It uses Molecule for testing Ansible scripts and it has automated builds in AWS EC2/CodeBuild and DockerHub. It can be used to develop, test and deploy complicated, multi-machine, multi-operating-system automated installs of software. Aurora's purpose is to unify one-liners approaches based on Ansible best practices.

For example, it's possible to use Aurora to install Docker, download the specified image and create a new container for you. It will also create a desktop icon to start the container and launch the hand.

Ansible user guide is available [here](https://docs.ansible.com/ansible/latest/user_guide/index.html) (We are currently using Ansible 2.8.1)

Molecule user guide is available [here](https://molecule.readthedocs.io/en/stable/) (We are currently using Molecule 2.20.1)

For certain tests (e.g. AWS EC2 tests) and certain private docker images, contact the system administrator to ask for access

<a name="development"/>
## Development ##

The preferred way to develop code for this project is to pull a certain docker image with a lot of tools already installed and open a container in it, then clone the aurora GitHub repository inside it. It is not recommended to clone aurora directly on your local machine while you do development and testing.

Instructions how to access the docker image and container for development, see Development Docker section below

### Development Docker ###

The docker images used for aurora development are [here](https://cloud.docker.com/u/shadowrobot/repository/docker/shadowrobot/aurora-molecule-devel)

We are currently using the bionic tag

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

### Test creation ###

### Testing on real hardware ###

## Deployment ##

## Structure of files ##

### Common ###

### Products ###

### Dependencies ###

## Playbooks and possible command line arguments ##

### Playbook creation ###

### teleop_deploy ###

### docker_deploy ###

### configure_software ###

### install_software ###

### install_python3 ###

## Inventories ##

## Roles ##

## Molecule tests ##

### Docker tests ###

### AWS EC2 tests ###

## Syntax and rules ##



## Before running the docker_deploy playbook ##

Before setting up the docker container, ethercat_interface parameter for the hand needs to be discovered. In order to do so, after plugging the hand’s ethernet cable into your machine and powering it up, please run
```shell
sudo dmesg
```
command in the console. At the bottom, there will be information similar to the one below:
```shell
[490.757853] IPv6: ADDRCONF(NETDEV_CHANGE): enp0s25: link becomes ready
```
In the above example, ‘enp0s25’ is the ethercat_interface that is needed. 

## Playbooks ##
* docker_deploy : For Hand E/G/H software deployments on single laptop
* teleop_deploy : For deploying teleop software on multiple machines (server, control-machine, client, windows-machine)


## How to run docker_deploy playbook ##

Open a terminal with Ctrl+Alt+T and run:

```bash
bash <(curl -Ls bit.ly/run-aurora) docker_deploy option1=value1 option2=value2 option3=value3
```

Options for docker_deploy playbook are [here](ansible/inventory/local/group_vars/docker_deploy.yml)

## How to run teleop_deploy playbook ##

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

Also, for debugging (not using the master branch), you can add the following immediately after docker_deploy or teleop_deploy:

* --debug-branch name_of_aurora_repo_branch (e.g. --debug-branch F#SRC-2603_add_ansible_bootstrap)

Run a playbook against one or more members of that group using the --limit tag:

* --limit rules (e.g. --limit 'all:!server' please use single quotes. More details could be found 
[here](https://ansible-tips-and-tricks.readthedocs.io/en/latest/ansible/commands/#limit-to-one-or-more-hosts))

For assigning input and secure input to playbook variables you can use the tags: --read-input var1, var2, var3 ... and --read-secure secure_var1, secure_var2, secure_var3 ... respectively

* --read-input vars (e.g. --read-input docker_username - To allow aurora script to prompt for docker username)
* --read-secure secure_vars (e.g. --read_secure docker_password - To allow aurora script to prompt for docker password)

To begin with, the docker_deploy playbook checks the installation status of docker. If docker is not installed then a 
new clean installation is performed. If the required image is private, 
then a valid Docker Hub account with pull credentials from Shadow Robot's Docker Hub is required. Then, 
the specified docker image is pulled and a docker 
container is initialized. Finally, a desktop shortcut is generated. This shortcut starts the docker container and 
launches the hand.

Example:

```bash
bash <(curl -Ls bit.ly/run-aurora) docker_deploy product=hand_e ethercat_interface=enp0s25
```
