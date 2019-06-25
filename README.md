# Aurora project #

The main purpose of this subsystem is to unify one-liners approaches based on Ansible best practices. This one-liner is able to install Docker, download the specified image and create a new container for you. It will also create a desktop icon to start the container and launch the hand.

## Before running the docker-deploy playbook ##

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
* docker-deploy : For Hand E/G/H software deployments on single laptop
* teleop-deploy : For deploying teleop software on multiple machines (server, control-machine, client, windows-machine)


## How to run docker-deploy playbook ##

Open a terminal with Ctrl+Alt+T and run:

```bash
bash <(curl -Ls bit.ly/run-aurora) docker-deploy option1=value1 option2=value2 option3=value3
```

Options for docker-deploy playbook are [here](ansible/inventory/local/group_vars/docker-deploy.yml)

## How to run teleop-deploy playbook ##

Open a terminal with Ctrl+Alt+T and run:

```bash
bash <(curl -Ls bit.ly/run-aurora) teleop-deploy --inventory name_of_inventory option1=value1 option2=value2 option3=value3
```
name_of_inventory can be development, staging or production. If you are not sure which to use, use staging.

Inventories correspond to fixed IP addresses as shown here:
* [development](ansible/inventory/teleop/development)
* [staging](ansible/inventory/teleop/staging)
* [production](ansible/inventory/teleop/production)

Options for teleop-deploy playbook are here for the following machines:
* [server](ansible/inventory/teleop/group_vars/server.yml)
* [control-machine](ansible/inventory/teleop/group_vars/control-machine.yml)
* [client](ansible/inventory/teleop/group_vars/client.yml)
* [windows-machine](ansible/inventory/teleop/group_vars/windows-machine.yml)

Also, for debugging (not using the master branch), you can add the following immediately after docker-deploy or teleop-deploy:

* --debug-branch name_of_aurora_repo_branch (e.g. --debug-branch F#SRC-2603_add_ansible_bootstrap)

Run a playbook against one or more members of that group using the --limit tag:

* --limit rules (e.g. --limit 'all:!server' please use single quotes. More details could be found 
[here](https://ansible-tips-and-tricks.readthedocs.io/en/latest/ansible/commands/#limit-to-one-or-more-hosts))

For assigning input and secure input to playbook variables you can use the tags: --read-input var1, var2, var3 ... and --read-secure secure_var1, secure_var2, secure_var3 ... respectively

* --read-input vars (e.g. --read-input docker_username - To allow aurora script to prompt for docker username)
* --read-secure secure_vars (e.g. --read_secure docker_password - To allow aurora script to prompt for docker password)

To begin with, the docker-deploy playbook checks the installation status of docker. If docker is not installed then a 
new clean installation is performed. If the required image is private, 
then a valid Docker Hub account with pull credentials from Shadow Robot's Docker Hub is required. Then, 
the specified docker image is pulled and a docker 
container is initialized. Finally, a desktop shortcut is generated. This shortcut starts the docker container and 
launches the hand.

Example:

```bash
bash <(curl -Ls bit.ly/run-aurora) docker-deploy product=hand_e ethercat_interface=enp0s25
```
