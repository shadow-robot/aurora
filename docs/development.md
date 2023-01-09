# Table of Contents
- [Development](#development)
  * [Development Docker](#development-docker)
- [Testing](#testing)
  * [Test creation](#test-creation)
  * [Unlimited scroll in terminator](#unlimited-scroll-in-terminator)
  * [Testing with molecule_docker](#testing-with-molecule_docker)
  * [Debugging and Lint](#debugging-and-lint)
  * [Private docker images](#private-docker-images)
  * [Testing with molecule_ec2](#testing-with-molecule_ec2)
  * [Credentials](#credentials)
  * [Automatic tests](#automatic-tests)
  * [Testing on real hardware](#testing-on-real-hardware)
- [Templating](#templating)
- [Dependencies](#dependencies)
- [Playbooks](#playbooks)
  * [Playbook creation](#playbook-creation)
- [Inventories](#inventories)
- [Syntax and rules](#syntax-and-rules)
- [Special variables](#special-variables)
- [Tutorial 1 desktop icon](#tutorial-1-desktop-icon)
- [Troubleshooting](#troubleshooting)

# Development #

The recommended way to develop code for this project is to pull a certain docker image ([Development Docker](#development-docker)) with a lot of tools already installed and open a container of this image, then clone the aurora GitHub repository inside it. It is not recommended to clone aurora directly on your local machine while you do development and testing.

## Development Docker ##

The docker images used for aurora development are [here](https://gallery.ecr.aws/shadowrobot/aurora-molecule-devel).

Currently both bionic and focal tags are working well.

Use the tag that matches your host operating system.

The rest of the document assumes the user is using bionic tag.

Instructions on how to use this:
1. Use Ubuntu 20.04 computer

2. Install Docker (using instructions from [here](https://docs.docker.com/install/linux/docker-ce/ubuntu/))

3. Run the following command in terminal to create a container for aurora development:

```
docker run -it --name aurora_dev -e DISPLAY -e QT_X11_NO_MITSHM=1 -e LOCAL_USER_ID=$(id -u) -v /var/run/docker.sock:/var/run/docker.sock -v /tmp/.X11-unix:/tmp/.X11-unix:rw public.ecr.aws/shadowrobot/aurora-molecule-devel:focal
```
4. Once the container has launched, clone aurora to home directory:
```
git clone https://github.com/shadow-robot/aurora.git
```
5. Go into the aurora folder:
```
cd aurora
```
6. Open Visual Studio Code which is already installed inside the Docker container:
```
code .
```

# Testing #

## Test creation ##

Create test case for both docker in ansible/playbooks/molecule_docker/molecule folder and for AWS EC2 in ansible/playbooks/molecule_ec2/molecule folder. For additional molecule_docker tests, copy the folder structure from other tests and modify the .py, converge.yml and molecule.yml files in tests folder.For additional molecule_ec2 tests, copy the folder structure of another EC2 test and modify the molecule.yml file inside. The EC2 tests just run the same tests as the Docker tests, but they do it in AWS EC2, using virtual machines, not Docker.

## Unlimited scroll in terminator ##

Before executing any tests, it is very useful to make sure you have unlimited scroll in terminator, because Molecule produces a lot of debug logs. Follow these steps to enable it: right click on the Terminator -> Preferences -> Profiles -> Scrolling and select Infinite scrollback.

## Testing with molecule_docker ##

Once you have written your code for aurora in your branch, test it locally with Molecule first before pushing to GitHub.

There are some molecule_docker tests which require connecting to AWS to download files (such as downloading the hand manual). For this reason, before running any Molecule tests, ask the system administrator for your AWS access key and secret access key. Then, in the docker container terminal, type:
```
export AWS_ACCESS_KEY=your_key
export AWS_SECRET_KEY=your_secret
```

1. In the docker container terminal execute the following command:

```
cd /home/user/aurora/ansible/playbooks/molecule_docker
```

2. Start with testing only your test case, without extra debug statements:

```
molecule test -s name_of_your_test_case
```

3. Fix any errors. If you want more debug information, execute the following:
```
molecule --debug test -s name_of_your_test_case
```
The --debug flag produces a lot of information. Remember to scroll up to see any possible lint or other errors that might have occurred.

4. Now test all test cases to check for effects on other aurora components and knock-on-effects:
```
molecule test --all
```
5. Fix any errors. If you want more debug information, execute the following:
```
molecule --debug test all
```

6. Often it is useful to run Molecule in stages (create, converge, verify, login (if necessary), and finally destroy) for better debugging (so you can inspect every stage yourself). See [this](https://molecule.readthedocs.io/en/stable/usage.html) page, and do, for example:
```
molecule create -s name_of_your_test_case
molecule converge -s name_of_your_test_case
molecule verify -s name_of_your_test_case
molecule login -s name_of_your_test_case
molecule destroy -s name_of_your_test_case
```

## Debugging and Lint ##

1. For a successful test, Molecule requires that all lint checks (yaml lint, flake8 python lint and ansible lint) pass. The AWS EC2 build will fail if any lint check fails or if any Molecule test fails.

2. In the Molecule logs, do a text search for "error" or "error occurred" as well as "failure" and "fatal".

3. You can add the --debug flag after molecule for more debug information, but remember to scroll up to see any possible lint or other errors that might have happened.

4. It's useful to enable [Unlimited scroll in terminator](#unlimited-scroll-in-terminator)

## Private docker images ##

At the moment, we don't want to give Molecule access to private docker hub / AWS private ECR credentials for private docker images (e.g. shadow-teleop). That is why, in every converge.yml inside the test cases in the molecule_docker folder, we override the image with image="public.ecr.aws/shadowrobot/dexterous-hand" for any teleop-related test cases. When we actually deploy Aurora, the user will be asked to fill in their private Docker hub credentials.

## Testing with molecule_ec2 ##

Once you have written your code for aurora in your branch, and tested it locally with molecule_docker, you can test it with AWS EC2 (initiated from local), by following the steps here:

## Credentials ##

1. Ask the system administrator for your AWS access key and secret access key. Then, in the docker container terminal, type:

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

2. Start with testing only your test case, without extra debug statements:

```
molecule test -s name_of_your_test_case
```

3. Fix any errors. If you want more debug information, execute the following:
```
molecule --debug test -s name_of_your_test_case
```
The --debug flag produces a lot of information. Remember to scroll up to see any possible lint or other errors that might have occurred.

4. Now test all test cases to check for effects on other aurora components and knock-on-effects:
```
molecule test --all
```
5. Fix any errors. If you want more debug information, execute the following:
```
molecule --debug test all
```

6. Often it is useful to run Molecule in stages (create, converge, verify, login (if necessary), and finally destroy) for better debugging (so you can inspect every stage yourself). See [this](https://molecule.readthedocs.io/en/stable/usage.html) page, and do, for example:
```
molecule create -s name_of_your_test_case
molecule converge -s name_of_your_test_case
molecule verify -s name_of_your_test_case
molecule login -s name_of_your_test_case
molecule destroy -s name_of_your_test_case
```
## Automatic tests ##

The buildspec.yml file in the root of the project defines what AWS CodeBuild should run when a PR is created or updated or when a daily build runs. It is configured to run all tests in /ansible/playbooks/molecule_ec2 folder. AWS buildspec specification is [here](https://docs.aws.amazon.com/codebuild/latest/userguide/build-spec-ref.html)

Note that AWS EC2 tests take about 1 hour to complete a build due to provisioning a new AWS virtual machines for each test and for each test running in a separate virtual machine and each virtual machine needing to pull the right Docker images and then execute the tests

## Testing on real hardware ##

For debugging (not using the master branch), you can add the following immediately after playbook name (for example docker_deploy or teleop_deploy):

* --branch name_of_aurora_repo_branch (e.g. --branch F#SRC-2603_add_ansible_bootstrap)

## Templating ##

For various bash/docker/etc. scripts, it's often useful to use Jinja2 templates (.j2 files). You can read more about .j2 files [here](https://docs.ansible.com/ansible/latest/user_guide/playbooks_templating.html)). They are stored either in /products/common/resources/ or if they are specific to a particular product, they should be in that products /templates/scripts folder.

## Dependencies ##

There are 2 main way of including dependencies in Ansible roles. The preferred way we use is the "include_role" method because it is dynamic (see [here](https://docs.ansible.com/ansible/latest/modules/include_role_module.html) for documentation).

E.g. if we want to include a particular role to install Docker, we do:

```bash
- name: Include installation/docker role
  include_role:
    name: installation/docker
```
The other way of having dependencies in Ansible is by using the meta folder and main.yml inside the meta folder. Please note: any meta dependencies are static only and will not take into account any group_vars or dynamic variables. That means that meta dependencies will only use the default/main.yml default value, nothing else. Any tasks in meta/main.yml are run before the task/main.yml. An example of meta/main.yml:

```bash
dependencies:
  - { role: installation/aws-cli-v2 }
```

# Playbooks #

Playbooks are "the main thing that runs"/"main executable" in Aurora. 

From the Ansible [website](https://docs.ansible.com/ansible/latest/user_guide/playbooks_intro.html): "Playbooks are the basis for a really simple configuration management and multi-machine deployment system, unlike any that already exist, and one that is very well suited to deploying complex applications."

## Playbook creation ##

Create your playbook in ansible/playbooks folder. It has be a .yml file with no hyphens (underscores are allowed).

You can read more about playbooks [here](https://docs.ansible.com/ansible/latest/user_guide/playbooks_intro.html)

It has to have a similar structure to this (let's say your playbook is called "my_playbook")

```bash
---

- name: Install Python 3
  import_playbook: ./install_python3.yml

- name: Install product Docker container and icons
  hosts: docker_deploy
  pre_tasks:

    - name: include products/common/validation role
      include_role:
        name: products/common/validation
      vars:
        playbook: "docker_deploy"
    
    - name: Running playbook setup role
      include_role:
        name: installation/playbook_setup
      when: not skip_molecule_task|bool

    - name: check if customer_key is provided and not false
      when: customer_key is defined and customer_key | length > 0
      set_fact:
        use_aws: true

  roles:
    - { role: products/common/get-system-variables }
    - { role: products/hand-e/docker-deploy/deploy }
    - { role: products/common/dolphin-icons, when: ansible_distribution_release|string == 'focal' or ansible_distribution_release|string == 'jammy'}
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
    - { role: products/common/get-system-variables }
    - { role: products/hand-e/docker-deploy/deploy }
    - { role: products/common/dolphin-icons, when: ansible_distribution_release|string == 'focal' or ansible_distribution_release|string == 'jammy' }
```

# Inventories #

An inventory is a file with group names and fixed IP addresses and some limited connection-related variables of the machines where we want the playbook to run. The inventory group names are required in playbooks in the hosts parameter (e.g. hosts: all). You can read more about hosts in playbooks [here](https://docs.ansible.com/ansible/latest/user_guide/playbooks_intro.html#hosts-and-users)

Inventories for teleop correspond to fixed IP addresses as shown here:
* [staging_b](ansible/inventory/teleop/staging_b)
* [staging_a](ansible/inventory/teleop/staging_a)
* [production](ansible/inventory/teleop/production)
* [simulation](ansible/inventory/teleop/simulation)

More information available [here](https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html)

# Syntax and rules #

1. Use lower case, words_separated_by_underscore file, folder, task, role, inventory group, playbook and any other names
2. Spaces are very important! Don't leave extra, unnecessary spaces anywhere, but also remember to add a newline to the end of all files
3. Follow [this](https://docs.ansible.com/ansible/latest/reference_appendices/YAMLSyntax.html) YAML syntax, paying special attention to the "Gotchas" [here](https://docs.ansible.com/ansible/latest/reference_appendices/YAMLSyntax.html#gotchas)

# Special variables #

Ansible has several special variables which can be accessed in playbooks, roles and tasks. E.g. if the special variable is ansible_user, you can access it using {{ ansible_user }}. Full list of special variables is [here](https://docs.ansible.com/ansible/latest/reference_appendices/special_variables.html)

# Tutorial 1 desktop icon #

Aim: to create a branch of aurora which has an Ansible role to install a desktop icon. When the user clicks on the desktop icon, a terminal window will open and say: "Hello, User!". The user can supply a different username as an extra vars parameter, so e.g. if the user runs the playbook with username=Peter, the terminal window will show "Hello, Peter!"

Requirements: you need a laptop/PC with internet, Ubuntu 18.04 or 20.04 installed.

Steps:

1. Go to [Development Docker](#development-docker) section and follow instructions there to set up your development environment

2. Create your own branch of aurora (from master). You can call your branch: Tutorial_YourName

3. Follow instructions in the [Playbook creation](#playbook-creation) section to create your own playbook, you can call it tutorial_icon_deploy.yml. Remember use the Install Python3 import as documented in [Playbook creation](#playbook-creation) and include a roles section. Your playbook should look something like this (yes, use hosts: docker_deploy for this tutorial):

```bash
---

- name: Install Python 3
  import_playbook: ./install_python3.yml

- name: Tutorial 1 installation
  hosts: docker_deploy
  roles:
    - {role: products/tutorial/deploy }
```

4. Create a role in roles/products/tutorial folder (you will have to create the tutorial folder). Inside the tutorial folder, create the following folder structure and empty files where indicated. You should have the following file structure:

 ![Folder structure](docs/images/folder_structure.png)

5. You deploy/defaults/main.yml should look like this:
```bash
---
user: "{{ ansible_user_id }}"
user_folder: "/home/{{ user }}"

```
6. Your deploy/tasks/main.yml should look like this:
```bash
---
- name: Include products/tutorial/desktop-icons role
  include_role:
    name: products/tutorial/desktop-icons
```
7. Your desktop-icons/defaults/main.yml should look like this:
```bash
---
user: "{{ ansible_user_id }}"
user_folder: "/home/{{ user }}"
username: "{{ user }}"
tutorial_launcher_folder: "{{ user_folder }}/.tutorial/tutorial_1"
```
8. Your desktop-icons/tasks/main.yml should look like this:
```bash
---
- name: Ensures that Desktop folder exists
  file:
    path: "{{ desktop_path }}"
    mode: '755'
    state: directory

- name: Ensures that tutorial directory exists
  file:
    path: "{{ tutorial_launcher_folder }}"
    state: directory

- name: Copy the tutorial desktop icon
  copy: 
    src: files/tutorial_1_icon.png
    dest: "{{ tutorial_launcher_folder }}/tutorial_1_icon.png"
    mode: '664'

- name: Create the executable launch script
  template:
    src: templates/scripts/show_terminal.j2
    dest: "{{ tutorial_launcher_folder }}/show_terminal.sh"
    mode: '755'

- name: Create the tutorial desktop icon
  template:
    src: ../../../common/resources/templates/desktop-icons/standard-icon.j2
    dest: "{{ desktop_path }}/Launch_Tutorial_1.desktop"
    mode: '755'
  vars:
    desktop_shortcut_name: Launch_Tutorial_1
    comment: "This is application launches Tutorial 1 of Aurora"
    folder: "{{ tutorial_launcher_folder }}"
    shell_script_file_name: show_terminal.sh
    icon_file_name: tutorial_1_icon.png

- name: Make Desktop icon trusted
  shell: gio set "{{ desktop_path }}/Launch_Tutorial_1.desktop" "metadata::trusted" yes
  when:
    - ansible_distribution|string == 'Ubuntu'
    - ansible_distribution_release|string == 'bionic'
    - not skip_molecule_task|bool
```
9. Download a suitable image (.jpg or .png) (e.g min 64x64 resolution, max 1000x1000 resolution) from the internet to be your tutorial_1_icon.png (or .jpg but then remember to change the extension to .jpg in your Ansible scripts as well). Place this image in the desktop-icons/files folder

10. Your desktop-icons/templates/scripts/show_terminal.j2 should look like this:
(you can read more about .j2 files in [Templating](#templating))
```bash
#jinja2: trim_blocks:False
#! /bin/bash
echo -e \"Hello, {{ username }}!\"
sleep infinity

```
11. Now, let's add a Molecule test, which tests if the desktop icon exists. In /playbooks/molecule_docker folder, copy an existing folder (e.g. teleop_empty_server_docker) and paste it and then change the name to e.g. tutorial_1_docker. Inside tutorial_1_docker folder you should have the following folders and files (change file and folder names when necessary)

 ![Docker test structure](docs/images/tutorial_1_docker.png)

12. You don't need to edit the Dockerfile.j2. Just edit the molecule.yml so it looks like this:
```bash
---
driver:
  name: docker
lint: |
  set -e
  yamllint .
  ansible-lint
  flake8
platforms:
  - name: tutorial_1_docker
    image: public.ecr.aws/shadowrobot/aurora-test-ubuntu-docker:focal
    groups:
      - docker_deploy
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:rw
provisioner:
  name: ansible
  env:
    ANSIBLE_ROLES_PATH: ../../../../roles
    AWS_ACCESS_KEY: ${AWS_ACCESS_KEY}
    AWS_SECRET_KEY: ${AWS_SECRET_KEY}
  inventory:
    links:
      group_vars: ../../../../inventory/local/group_vars
verifier:
  name: testinfra
scenario:
  create_sequence:
    - create
  check_sequence:
    - destroy
    - create
    - converge
    - check
    - destroy
  converge_sequence:
    - create
    - converge
  destroy_sequence:
    - destroy
  test_sequence:
    - lint
    - destroy
    - syntax
    - create
    - converge
    - idempotence
    - verify
    - destroy
```
13. Edit the converge.yml so it looks like this:
```bash
---
- name: Tutorial 1 playbook
  import_playbook: ../../../tutorial_icon_deploy.yml

```

14. Edit the test_tutorial_1.py so it looks like this (we are using a general pattern here, which is why we have for loops for icons and scripts).
```bash
import os
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_icons_in_docker(host):
    desktop_path = '/home/' + str(host.user().name) + '/Desktop/'
    script_path = '/home/' + str(host.user().name) + \
                  '/.tutorial/tutorial_1/'
    icons = (
        'Launch_Tutorial_1'
        )
    scripts = (
        'show_terminal'
        )
    for icon in icons:
        assert host.file(desktop_path+icon+'.desktop').exists
    for script in scripts:
        assert host.file(script_path+script+'.sh').exists

```
15. Now that your Docker test is ready, create the EC2 test which tests if the desktop icon exists, but it runs on an AWS virtual machine (not in Docker). In /playbooks/molecule_ec2 folder, copy an existing folder (e.g. teleop_server_chrony_ec2) and paste it and then change the name to e.g. tutorial_1_ec2. Inside tutorial_1_ec2 folder you should have the following folders and files (change file and folder names when necessary):

 ![EC2 test structure](docs/images/molecule_ec2_tutorial.png)

16. Edit the molecule.yml so it looks like this:
```bash
---
dependency:
  name: galaxy
driver:
  name: ec2
lint: |
  set -e
  yamllint .
  ansible-lint
  flake8
platforms:
  # Adding CODEBUILD_BUILD_ID to instance name in order to allow parallel EC2 execution of tests from CodeBuild
  - name: tutorial_1_ec2_${CODEBUILD_BUILD_ID}
    image: ami-0820357ff5cf2333d
    instance_type: t2.micro
    region: eu-west-2
    vpc_id: vpc-0f8cc2cc245d57eb4
    vpc_subnet_id: subnet-0c8cfe80927f04845
    groups:
      - docker_deploy
provisioner:
  name: ansible
  env:
    ANSIBLE_ROLES_PATH: ../../../../roles
  connection_options:
    ansible_python_interpreter: /usr/bin/python3
  inventory:
    links:
      group_vars: ../../../../inventory/local/group_vars
  playbooks:
    create: ../resources/ec2/create.yml
    destroy: ../resources/ec2/destroy.yml
    prepare: ../../../install_python3.yml
    converge: ../../../molecule_docker/molecule/tutorial_1_docker/converge.yml
verifier:
  name: testinfra
  directory: ../../../molecule_docker/molecule/tutorial_1_docker/tests/
scenario:
  create_sequence:
    - dependency
    - create
    - prepare
  check_sequence:
    - dependency
    - destroy
    - create
    - prepare
    - converge
    - check
    - destroy
  converge_sequence:
    - dependency
    - create
    - prepare
    - converge
  destroy_sequence:
    - dependency
    - destroy
  test_sequence:
    - dependency
    - lint
    - destroy
    - syntax
    - create
    - prepare
    - converge
    - idempotence
    - verify
    - destroy

```
17. Now all the Ansible code is done and both Docker and EC2 tests added. Next step is to execute the Docker test locally: follow the steps here: [Testing with molecule_docker](#testing-with-molecule_docker) (you may want to use the -s flag to limit the test to your tutorial_1 test only. Normally we want to re-test everything for every introduced change, but it's pretty safe to say tutorial_1 hasn't broken other parts of Aurora)

18. After local Docker tests are complete, you can optionally run the EC2 triggered locally as well by following the steps here: [Testing with molecule_ec2](#testing-with-molecule_ec2) (However, you need to contact the System Administrator for credentials as explained here: [Credentials](#credentials))

19. When all tests are passing (initiated locally), create a PR of your branch and see the AWS automatic build activate as well as the AWS ECR tests (building aurora Docker images). All tests must pass before even thinking about merging to master (and in this exercise, please DO NOT MERGE to master!). More information available here: [Automatic tests](#automatic-tests)

20. Once your PR is passing (all green), you are ready to test your branch on real hardware. For this tutorial, you will test your branch on your own local machine by opening a terminal window by pressing Ctrl+Alt+T and run this:
```bash
bash <(curl -Ls bit.ly/run-aurora) tutorial_icon_deploy --branch NameOfYourBranch --inventory local/docker_deploy username=YourName
```
Rememeber to substitute in NameOfYourBranch and YourName

You will have to enter the sudo password for your computer twice (once for the bash script and once for ansible)

21. The desktop icon should be created and when you double-click on it, a window should pop up and greet you using the username you passed in. You have now completed Tutorial 1

  ![Tutorial 1 icon](docs/images/tutorial_1_icon.png)
 
  ![Tutorial 1 result](docs/images/tutorial_1_result.png)

# Troubleshooting #

1. **SSH warning** when using the same laptops for multiple different NUCs (in server_and_nuc_deploy and teleop_deploy): for a given server laptop, only 1 NUC is supposed to be used. If the NUC is changed, the SSH keys stored on the laptop don't match the NUC, so aurora has to be re-run. In this case, it's required that the user manually deletes the .ssh folder on the server laptop to clear ssh keys.

2. **Unable to connect to a new NUC with SSH** (not cloned from Clonezilla image) (in server_and_nuc_deploy and teleop_deploy): the NUC with Ubuntu Server 18.04 needs manual netplan configuration as below in order to recognize and connect the ethernet-USB adapters: edit the file /etc/netplan/50-cloud-init.yaml in the NUC host so it has the following:

```bash
network:
    version: 2
    ethernets:
        enx-usb-ethernet:
            match:
                name: enx*
            dhcp4: true
            optional: true
```

3. **Unable to launch RQT on NUC** (or other graphical programs running on the NUC), due to Xauthority issues (in server_and_nuc_deploy and teleop_deploy): Before running aurora, execute ssh -X user@nuc-control to create a proper .Xauthority file in the NUC host (user home folder). This is required before aurora runs and creates the container.
