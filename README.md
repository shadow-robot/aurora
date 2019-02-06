# Aurora project #

The main purpose of this subsystem is to unify one-liners approaches based on Ansible best practices. This one-liner is able to install Docker, download the specified image and create a new container for you. It will also create a desktop icon to start the container and launch the hand.

## Before running the docker-deploy playbook ##

Before setting up the docker container, ethercatinterface parameter for the hand needs to be discovered. In order to do so, after plugging the hand’s ethernet cable into your machine and powering it up, please run
```shell
sudo dmesg
```
command in the console. At the bottom, there will be information similar to the one below:
```shell
[490.757853] IPv6: ADDRCONF(NETDEV_CHANGE): enp0s25: link becomes ready
```
In the above example, ‘enp0s25’ is the ethercatinterface that is needed. 

## How to run docker-deploy playbook ##

Open a terminal with Ctrl+Alt+T and run:

```bash
bash <(curl -Ls bit.ly/run-ansible-sh) docker-deploy option1=value1 option2=value2 option3=value3
```

Possible options for the docker-deploy are:
"
* product                   Name of the product (hand_e or hand_h)
* image                     Name of the Docker hub image to pull
* reinstall                 Flag to know if the docker container should be fully reinstalled (default: false)
* name                      Name of the docker container
* ethercatinterface         Ethercat interface of the hand
* nvidia-docker             Enable nvidia-docker (default: false)
* desktopicon               Generates a desktop icon to launch the hand (default: true)
* configbranch              Specify the branch for the specific hand (Only for dexterous hand)
* shortcutname              Specify the name for the desktop icon (default: Shadow_Hand_Launcher)
* optoforce                 Specify if optoforce sensors are going to be used with a branch name (default: false)
* launchhand                Specify if hand driver should start when double clicking desktop icon (default: true)
* customerkey               Flag to prompt for customer key for uploading files to AWS (can be skipped or be set to true)
* cyberglove                Specify the branch of sr_cyberglove_config for cyberglove configuration (default: false)
* demo_icons                Generates desktop icons to run demos (default: false)"

Also, for debugging, you can add the following immediately after docker-deploy:

* --debug-branch name_of_the_debug_branch_of_aurora_repo (e.g. --debug-branch F#SRC-2603_add_ansible_bootstrap)

To begin with, the docker-deploy playbook checks the installation status of docker. If docker is not installed then a new clean installation is performed. If the required image is private, 
then a valid Docker Hub account with pull credentials from Shadow Robot's Docker Hub is required. Then, the specified docker image is pulled and a docker 
container is initialized. Finally, a desktop shortcut is generated. This shortcut starts the docker container and launches 
the hand.

Example:

```bash
bash <(curl -Ls bit.ly/run-ansible-sh) docker-deploy --debug-branch F#SRC-2603_add_ansible_bootstrap product=hand_e ethercatinterface=enp0s25
```
