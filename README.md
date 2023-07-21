# Table of Contents
- [Introduction](#introduction)
- [Multiple Aurora Installations on one device](#multiple-aurora-installations-on-one-device)
- [How to run](#how-to-run)
  * [teleop_deploy](#teleop_deploy)
  * [server_and_nuc_deploy](#server_and_nuc_deploy)
  * [docker_deploy](#docker_deploy)
  * [configure_software](#configure_software)
  * [install_software](#install_software)
  * [install_python3](#install_python3)
- [Structure of files](#structure-of-files)
  * [Roles](#roles)
  * [Docker](#docker)
  * [Installation](#installation)
  * [Products](#products)
  * [Common](#common)

# Other useful pages
- [Aurora Development Page](/docs/development.md)
- [Molecule Docker Page](/docs/molecule_dockers.md)

# Introduction #

Aurora is an installation automation tool using Ansible. It uses Molecule for testing Ansible scripts and it has automated builds in AWS EC2/CodeBuild/ECR. It can be used to develop, test and deploy complicated, multi-machine, multi-operating-system automated installs of software. Aurora's purpose is to unify one-liners approaches based on Ansible best practices.

For example, it's possible to use Aurora to install Docker, download the specified image and create a new container for you. It will also create a desktop icon to start the container and launch the hand.

Ansible user guide is available [here](https://docs.ansible.com/ansible/latest/user_guide/index.html) (Aurora is currently using Ansible 4.2.0)

Molecule user guide is available [here](https://molecule.readthedocs.io/en/latest/) (Aurora is currently using Molecule 3.6.1)

# Multiple Aurora Installations on one device #

We can now easily have multiple Aurora setups on one device, you simply need to define a unique name for the variable container_name by adding "container_name=new_container_name" to your oneliner when running each Aurora oneliner. This is because Aurora creates icons and scripts in the folder ".shadow_launcher_app_{container_name}" and stores shortcut to these icons at "{container_name}.desktop".

By having the name of the container attached to where we store the icons and scripts we can have more control over which icons get removed and reinstalled when rerunning Aurora, as we can just remove the folders that contain the containers name. This will leave the previous run's icons and scripts intact.

# How to run #

## teleop_deploy ##

If using real robots, teleop_deploy will deploy software on a laptop (called "server" in this playbook) and a control machine (NUC).

Teleop_deploy can also be used fully in simulation, in which case only 1 computer is required (called "server" in this playbook)

To begin with, the teleop_deploy playbook checks the installation status of docker. If docker is not installed then a new clean installation is performed. Then the specified docker image is pulled and a docker container is initialized. Finally, desktop shortcuts are generated. This shortcuts start the teleop software and run the arm(s) and the hand(s).

**How to run:**

You will first need to ensure that you have entered your customer_key into the one liner (used to pull the docker images), then a sudo_password (i.e. the password of the user with sudo permissions) for the laptop you are using to run this playbook, and also for the Vault password, which is provided by Shadow.

Open a terminal with Ctrl+Alt+T and run:

```bash
bash <(curl -Ls https://raw.githubusercontent.com/shadow-robot/aurora/{release_tag}}/bin/run-ansible.sh) teleop_deploy --branch {release_tag} --inventory name_of_inventory --read-secure customer_key option1=value1 option2=value2 option3=value3
```
name_of_inventory corresponds to fixed IP addresses as shown here:
* [development](ansible/inventory/teleop/development)
* [development_remote](ansible/inventory/teleop/development_remote)
* [production](ansible/inventory/teleop/production)
* [production_remote](ansible/inventory/teleop/production_remote)
* [simulation](ansible/inventory/teleop/simulation)

Example for real robots with haptx bimanual teleop:

```bash
bash <(curl -Ls https://raw.githubusercontent.com/shadow-robot/aurora/v2.1.7/bin/run-ansible.sh) teleop_deploy --branch v2.1.7 --inventory production --read-secure customer_key reinstall=true bimanual=true upgrade_check=true image="080653068785.dkr.ecr.eu-west-2.amazonaws.com/shadow-teleop-haptx-binary" tag="noetic-v0.0.23" glove="haptx" use_steamvr=false arm_ip_right="10.8.1.1" arm_ip_left="10.8.2.1" ethercat_right_arm="eno1" ethercat_left_arm="enx000ec6bfe175"
```

Example for simulated robots without a real vive system or real gloves: 

```bash
bash <(curl -Ls https://raw.githubusercontent.com/shadow-robot/aurora/v2.1.7/bin/run-ansible.sh) teleop_deploy --branch v2.1.7 --inventory simulation --read-secure customer_key reinstall=true upgrade_check=true image="080653068785.dkr.ecr.eu-west-2.amazonaws.com/shadow-teleop-haptx-binary" tag="noetic-v0.0.23" glove="haptx" real_glove=false real_vive=false
```

Options for teleop_deploy playbook are here for the following machines:
* [server](ansible/inventory/teleop/group_vars/server.yml)
* [control-machine](ansible/inventory/teleop/group_vars/control_machine.yml)
* [simulation](ansible/inventory/teleop/group_vars/simulation.yml)

Run a playbook against one or more members of that group using the --limit tag:

* --limit rules (e.g. --limit 'all:!server' - this would run ansible on all machines that aren't the server. Please use single quotes. More details could be found [here](https://ansible-tips-and-tricks.readthedocs.io/en/latest/ansible/commands/#limit-to-one-or-more-hosts))

For assigning input and secure input to playbook variables you can use the tags: --read-input var1, var2, var3 ... and --read-secure secure_var1, secure_var2, secure_var3 ... respectively

* --read-input vars (vars = comma-separated list, e.g. --read-input docker_username - To allow aurora script to prompt for docker username)
* --read-secure secure_vars (secure_vars = comma-separated list, e.g. --read_secure customer_key - To allow aurora script to prompt for customer key, to upload ROS logs and pull AWS docker images. Or e.g. --read-secure docker_password,customer_key - To allow aurora script to prompt for docker password and customer_key)

**VAULT password:**

Shadow will supply you with the Vault password, which is needed to decrypt some credentials to access the NUC.

## server_and_nuc_deploy ##

For Hand E software deployments on a laptop (called "server" in this playbook) and a control machine (NUC)

To begin with, the server_and_nuc_deploy playbook checks the installation status of docker. If docker is not installed then a new clean installation is performed. If the required image is private, then a valid customer_key is required. Then the specified docker image is pulled and a docker container is initialized. Finally, a desktop shortcut is generated. This shortcut starts the docker container and launches the hand.

Within the server_and_nuc playbook you can install 3 types of shadow products, hand_e, hand_lite, hand_extra_lite on their own, hand_e and arm and hand_e and glove.
The variables that you set when running the playbook determine the icons created. For example setting product=glove_hand_e uses the
hand and glove product, or setting product=arm_hand_e will install the hand and arm product.

**How to run:**

You will be asked for a sudo_password (i.e. the password of the user with sudo permissions) for the laptop you are using to run this playbook, and also for the Vault password, which is provided by Shadow.

Open a terminal with Ctrl+Alt+T and run:

```bash
bash <(curl -Ls https://raw.githubusercontent.com/shadow-robot/aurora/v2.2.0/bin/run-ansible.sh) server_and_nuc_deploy --branch v2.2.0 --read-secure customer_key option1=value1 option2=value2 option3=value3
```

Example:

```bash
bash <(curl -Ls https://raw.githubusercontent.com/shadow-robot/aurora/v2.2.0/bin/run-ansible.sh) server_and_nuc_deploy --branch v2.2.0 --read-secure customer_key product=hand_e tag="noetic-v1.0.26"
```
Inventories correspond to fixed IP addresses as shown here:
* [development](ansible/inventory/server_and_nuc/development)
* [production](ansible/inventory/server_and_nuc/production)

Options for server_and_nuc_deploy playbook are here for the following machines:
* [server](ansible/inventory/server_and_nuc/group_vars/server.yml)
* [control-machine](ansible/inventory/server_and_nuc/group_vars/control_machine.yml)

Run a playbook against one or more members of that group using the --limit tag:

* --limit rules (e.g. --limit 'all:!server' - this would run ansible on all machines that aren't the server. Please use single quotes. More details could be found [here](https://ansible-tips-and-tricks.readthedocs.io/en/latest/ansible/commands/#limit-to-one-or-more-hosts))

For assigning input and secure input to playbook variables you can use the tags: --read-input var1, var2, var3 ... and --read-secure secure_var1, secure_var2, secure_var3 ... respectively

* --read-input vars (vars = comma-separated list, e.g. --read-input docker_username - To allow aurora script to prompt for docker username)
* --read-secure secure_vars (secure_vars = comma-separated list, e.g. --read_secure customer_key - To allow aurora script to prompt for customer key, to upload ROS logs and pull AWS docker images. Or e.g. --read-secure docker_password,customer_key - To allow aurora script to prompt for docker password and customer_key)

**VAULT password:**

Shadow will supply you with the Vault password, which is needed to decrypt some credentials to access the NUC.


### Hand and Arm ###
Hand and Arm is one of the main use-cases of the server_and_nuc playbook. It requires more variables to be passed in then just using hand_e on its own. The main variables that need to be set are related to the arms themselves, mainly the variables ethercat_right/left_arm variable and arm_ip_right/left. But also the product type needs to be defined as product=arm_hand_e.

Example:

```bash
bash <(curl -Ls https://raw.githubusercontent.com/shadow-robot/aurora/v2.2.4/bin/run-ansible.sh) server_and_nuc_deploy --branch v2.2.4 --read-secure customer_key reinstall=true bimanual=true product="arm_hand_e" image="public.ecr.aws/shadowrobot/dexterous-hand" tag="noetic-v1.0.29" arm_ip_right="10.8.1.1" arm_ip_left="10.8.2.1" ethercat_right_arm="eno1" ethercat_left_arm="enx000ec6bfe175"
```

### Hand and Glove ###
Hand and Glove is another main product of the server_and_nuc playbook. This also takes in a new product type with product=glove_hand_e now, it also has extra parameters relating to the glove that you are using for the product. These variables are found in ansible/inventory/server_and_nuc/group_vars. The hand and glove specific variables are glove, real_glove and polhemus_type. Another thing to denote about this product is that it's not based on the dexterous-hand image, but instead the shadow-dexterous-hand-glove image.

Example:

```bash
bash <(curl -Ls https://raw.githubusercontent.com/shadow-robot/aurora/v2.1.7/bin/run-ansible.sh) server_and_nuc_deploy --branch v2.1.7 --read-secure customer_key reinstall=true bimanual=true product="glove_hand_e" image="080653068785.dkr.ecr.eu-west-2.amazonaws.com/shadow-dexterous-hand-glove" tag="noetic-v0.0.8" glove="shadow_glove" polhemus_type="viper"
```

## docker_deploy ##

For Hand E software deployments on single laptop.

To begin with, the docker_deploy playbook checks the installation status of docker. If docker is not installed then a new clean installation is performed. If the required image is private, then a valid customer_key is required. Then the specified docker image is pulled and a docker container is initialized. Finally, a desktop shortcut is generated. This shortcut starts the docker container and launches the hand.

**How to run:**

Open a terminal with Ctrl+Alt+T and run:

```bash
bash <(curl -Ls https://raw.githubusercontent.com/shadow-robot/aurora/v2.2.0/bin/run-ansible.sh) docker_deploy --branch v2.2.0 option1=value1 option2=value2 option3=value3
```

Example:

```bash
bash <(curl -Ls https://raw.githubusercontent.com/shadow-robot/aurora/v2.2.0/bin/run-ansible.sh) docker_deploy --branch v2.2.0 product=hand_e tag=noetic-v1.0.26
```
Options for docker_deploy playbook are [here](ansible/inventory/local/group_vars/docker_deploy.yml)

For assigning input and secure input to playbook variables you can use the tags: --read-input var1, var2, var3 ... and --read-secure secure_var1, secure_var2, secure_var3 ... respectively

* --read-input vars (vars = comma-separated list, e.g. --read-input docker_username - To allow aurora script to prompt for docker username)
* --read-secure secure_vars (secure_vars = comma-separated list, e.g. --read_secure customer_key - To allow aurora script to prompt for customer key, to upload ROS logs and pull AWS docker images. Or e.g. --read-secure docker_password,customer_key - To allow aurora script to prompt for docker password and customer_key)

**BECOME password:**

If you are prompted for a BECOME password, enter the sudo password of the computer you are using. 

## configure_software ##

This runs the docker/setup-ui role (details are [here](ansible/roles/docker/setup-ui/tasks/main.yml) when it is passed a list of software which includes 'setup-docker'. This is used in the AWS ECR Docker image builds for Aurora.

**How to run:**

Open a terminal with Ctrl+Alt+T and run:

```bash
bash <(curl -Ls bit.ly/run-aurora) configure_software software=['setup-docker']
```

## install_software ##

This installs software based on external parameters (details are [here](https://github.com/shadow-robot/aurora/blob/master/ansible/playbooks/install_software.yml) when it is passed a list of software. This is used in the AWS ECR Docker image builds for Aurora and also builds of shadow-teleop Docker images

**How to run:**

Open a terminal with Ctrl+Alt+T and run:

```bash
bash <(curl -Ls bit.ly/run-aurora) install_software software=['software1','software2','software3']
```
Example:

```bash
bash <(curl -Ls bit.ly/run-aurora) install_software software=['docker','aws-cli']
```

## install_python3 ##

This installs the default Python3 for Ubuntu 18.04 and 20.04 (Python 3.8.10). Details [here](https://github.com/shadow-robot/aurora/blob/master/ansible/playbooks/install_python3.yml). It also sets ansible_python_interpreter correctly for Python3 

**How to run:**

Open a terminal with Ctrl+Alt+T and run:

```bash
bash <(curl -Ls bit.ly/run-aurora) install_python3
```

# Structure of files #

# Roles #

Everything you need to do in Ansible is achieved using roles. Roles basically mean: "execute this set of tasks" (defined in the role's tasks/main.yml file). The roles folder is very important and contains roles and tasks for teleop, hand_e and a common role section. It is very important that you re-use existing roles whenever possible to avoid code duplication. Please read about roles [here](https://docs.ansible.com/ansible/latest/user_guide/playbooks_reuse_roles.html) 

The roles folder contains the following sub-folders:

[Docker](#docker)

[Installation](#installation)

[Products](#products)


## Docker ##

The docker folder contains some general roles that are used after docker install. It has the following folders:

 - aws: this is used for installing our shadow-upload.sh script and AWS customer key which uploads ROS logs to AWS. It has a dependency of installation/aws-cli

 - ecr: this role is used to pull the login credentials from AWS to allow Aurora to login to AWS CLI and authenticate with DockerHub so that you can pull our private and public ECR images.

 - docker-image: this is used for pulling the docker image (nvidia_docker [group_var](ansible/inventory/teleop/group_vars/server.yml) is a boolean which specifies whether nvidia-container-toolkit should be used)

 - setup-ui: this is used to install various UI libraries, terminator, vim, git, subversion, bash-completion, etc., to create the /usr/local/bin/entrypoint.sh file and setting up a new Docker user

## Installation ##

Any programs that need to be installed are placed in the installation role. It has the following folders:

 - aws-cli-v2
 - chrome
 - chrony-client
 - chrony-server
 - dhcp
 - docker
 - install_common_tools
 - install_licence_tools
 - libglvnd
 - lxml
 - mongodb
 - mplabx
 - net-tools
 - nvidia-docker
 - prepareshadowvpn
 - production_tools
 - pycharm
 - qtcreator
 - rabbitvcs
 - resolvconf
 - shadow_glove_driver
 - steamvr
 - vscode
 - warehouse_ros

## Products ##

The Products folder (/ansible/roles/products) contains groupings of roles under folders:

 - common
 - hand-e
 - teleop

The logic is: everything to do with hand-e is in the hand-e folder, everything to do with teleop is in the teleop folder.
The common product is special, see below.

## Common ##

The common role contains any common task or roles that is used repeatedly in many different products. 

It contains the following roles:

 - arm-interfaces
 - bimanual-icons
 - clear-icons
 - close-everything-icon
 - default-icon
 - default-icon-no-terminator
 - demo-icons
 - docker-container
 - dolphin-icons
 - get-system-variables
 - hand_config
 - hand-manual
 - local-hand-launch
 - local-zero-force-mode-launch
 - record-hand-data
 - resources
 - roslaunch-icon
 - save-logs-icons
 - validation
 - web-gui-icon

For example, since docker-container contains the Ansible scripts for creating a Docker container, and it is a very common task shared by many products, it makes sense to have it in common so it can be referred to by other products.

Whenever you create a role, if it will likely be used by other products (e.g. it's not very specific to your product), please put it under common roles, or if it's for installing some commonly used program, put it under installation.
