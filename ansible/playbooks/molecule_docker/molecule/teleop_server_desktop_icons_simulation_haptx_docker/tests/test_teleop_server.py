import os
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')

def test_icons_in_docker(host):
    desktop_path = '/home/' + str(host.user().name) + '/Desktop/'
    script_path = '/home/' + str(host.user().name) + \
                  '/.shadow_launcher_app/shadow_hand_launcher/'
    save_logs_script_path = '/home/' + str(host.user().name) + \
                            '/.shadow_save_log_app/save_latest_ros_logs/'
    icons = (
        'Launch Shadow Right Teleop',
        'Launch Shadow Left Teleop',
        'Launch Shadow Bimanual Teleop',
        'Shadow NUC RQT',
        'Shadow Advanced Launchers/1 - Launch Server Container',
        'Shadow Advanced Launchers/2 - Launch Server ROSCORE',
        'Shadow Advanced Launchers/3 - Launch NUC Right ' +
        'Side Teleop Hardware Control Loop',
        'Shadow Advanced Launchers/3 - Launch NUC Left ' +
        'Side Teleop Hardware Control Loop',
        'Shadow Advanced Launchers/3 - Launch NUC Bimanual ' +
        'Teleop Hardware Control Loop',
        'Shadow Advanced Launchers/3 - Demohand A Launch NUC ' +
        'Right Side Teleop Hardware Control Loop',
        'Shadow Advanced Launchers/3 - Demohand B Launch NUC ' +
        'Right Side Teleop Hardware Control Loop',
        'Shadow Advanced Launchers/3 - Demohand C Launch NUC ' +
        'Right Side Teleop Hardware Control Loop',
        'Shadow Advanced Launchers/3 - Demohand D Launch NUC ' +
        'Left Side Teleop Hardware Control Loop',
        'Shadow Advanced Launchers/4 - Launch Right Teleop GUI',
        'Shadow Advanced Launchers/4 - Launch Left Teleop GUI',
        'Shadow Advanced Launchers/4 - Launch Bimanual Teleop GUI',
        'Shadow Advanced Launchers/5 - Launch Right HaptX Mapping',
        'Shadow Advanced Launchers/5 - Launch Left HaptX Mapping',
        'Shadow Advanced Launchers/5 - Launch Bimanual HaptX Mapping',
        'Shadow Advanced Launchers/Launch NUC Container',
        'Shadow Demos/Close Right Hand',
        'Shadow Demos/Demo Right Hand',
        'Shadow Demos/Open Right Hand',
        'Shadow Demos/Close Left Hand',
        'Shadow Demos/Demo Left Hand',
        'Shadow Demos/Open Left Hand',
        'Shadow ROS Logs Saver and Uploader',
        'Teleop Documentation',
        'Shadow System Monitor',
        'Bimanual HaptX Teleop Simulation'
        )
    scripts = (
        'shadow_launch_right_teleop_sim.sh',
        'shadow_launch_left_teleop_sim.sh',
        'shadow_launch_bimanual_teleop_sim.sh',
        'shadow_server_container',
        'shadow_roscore',
        'shadow_nuc_right_hardware_control_loop',
        'shadow_nuc_left_hardware_control_loop',
        'shadow_nuc_bimanual_hardware_control_loop',
        'teleop_exec_A',
        'teleop_exec_B',
        'teleop_exec_C',
        'teleop_exec_D',
        'shadow_GUI_left',
        'shadow_GUI_right',
        'shadow_GUI_bimanual',
        'shadow_haptx_mapping_launch_right',
        'shadow_haptx_mapping_launch_left',
        'shadow_haptx_mapping_launch_bimanual',
        'shadow_nuc_container',
        'close_right_hand',
        'demo_right_hand',
        'open_right_hand',
        'close_left_hand',
        'demo_left_hand',
        'open_left_hand',
        'shadow_launcher_doc_exec',
        'shadow_launcher_system_monitor_exec',
        'shadow_sim_demo'
        )
    for icon in icons:
        assert host.file(desktop_path+icon+'.desktop').exists
    for script in scripts:
        assert host.file(script_path+script+'.sh').exists
    save_logs_file = save_logs_script_path+'save-latest-ros-logs.sh'
    assert host.file(save_logs_file).exists
    hand_manual_file = desktop_path+'Palm_EDC_User_Manual_1.7.pdf'
    assert host.file(hand_manual_file).exists



sdfdsffsdfs


---
- name: Install desktop icon for launching Shadow Right Teleop Simulation
  import_tasks: default-icon-no-terminator.yml
  vars:
    desktop_icon_png: "hand-e.png"
    launch_script: "shadow_launch_right_teleop_sim.sh"
    desktop_icon_name: "Launch Shadow Right Teleop Simulation"
    template: templates/scripts/launch-teleop-right-sim.j2
    desktop_icon_path: "Launch Shadow Right Teleop Simulation"
    launch_terminal: "false"

- name: Install desktop icon for launching Shadow Left Teleop Simulation
  import_tasks: default-icon-no-terminator.yml
  vars:
    desktop_icon_png: "hand-e-left.png"
    launch_script: "shadow_launch_left_teleop_sim.sh"
    desktop_icon_name: "Launch Shadow Left Teleop Simulation"
    template: templates/scripts/launch-teleop-left-sim.j2
    desktop_icon_path: "Launch Shadow Left Teleop Simulation"
    launch_terminal: "false"

- name: Install desktop icon for launching Shadow Bimanual Teleop Simulation
  import_tasks: default-icon-no-terminator.yml
  vars:
    desktop_icon_png: "hand-e-bimanual.png"
    launch_script: "shadow_launch_bimanual_teleop_sim.sh"
    desktop_icon_name: "Launch Shadow Bimanual Teleop Simulation"
    template: templates/scripts/launch-teleop-bimanual-sim.j2
    desktop_icon_path: "Launch Shadow Bimanual Teleop Simulation"
    launch_terminal: "false"

- name: Include hand-manual role
  include_role:
    name: products/common/hand-manual
  when: customer_key is defined and customer_key | length > 0

- name: Install the Teleop Documentation desktop icon for HaptX
  include_tasks: web-gui-icon.yml
  vars:
    desktop_icon_png: "documentation_icon.png"
    launch_script: "shadow_launcher_doc_exec.sh"
    local_website_port_var: '7070'
    desktop_icon_name: "Teleop Documentation"
    desktop_icon_path: "Teleop Documentation"
    launch_terminal: "true"
    start_container_var: "true"
    start_server_command_var: "roslaunch sr_teleop_haptx_documentation sr_teleop_haptx_documentation_server.launch port:={{ local_website_port_var }}"
    preconditions_var: ""
  when: glove=="haptx"

- name: Install the Teleop Documentation desktop icon for polhemus
  include_tasks: web-gui-icon.yml
  vars:
    desktop_icon_png: "documentation_icon.png"
    launch_script: "shadow_launcher_doc_exec.sh"
    local_website_port_var: '7070'
    desktop_icon_name: "Teleop Documentation"
    desktop_icon_path: "Teleop Documentation"
    launch_terminal: "true"
    start_container_var: "true"
    start_server_command_var: "roslaunch sr_teleop_polhemus_documentation sr_teleop_polhemus_documentation_server.launch port:={{ local_website_port_var }}"
    preconditions_var: ""
  when: glove=="polhemus"

- name: Install the Shadow System Monitor desktop icon for Teleop
  include_tasks: web-gui-icon.yml
  vars:
    desktop_icon_png: "system_monitor.png"
    launch_script: "shadow_launcher_system_monitor_exec.sh"
    local_website_port_var: '8081'
    desktop_icon_name: "Shadow System Monitor"
    desktop_icon_path: "Shadow System Monitor"
    launch_terminal: "true"
    start_container_var: "false"
    start_server_command_var: ""
    preconditions_var: "Launch Shadow Teleop icon"

- name: Create Shadow Demos folder
  file:
    path: "{{ user_folder }}/Desktop/Shadow Demos"
    mode: '755'
    state: directory

- name: Create Shadow Advanced Launchers folder
  file:
    path: "{{ user_folder }}/Desktop/Shadow Advanced Launchers"
    mode: '755'
    state: directory

- name: Install desktop icon for server container
  include_tasks: default-icon.yml
  vars:
    template: ../../../common/resources/templates/scripts/start-docker-container.j2
    desktop_icon_png: "laptop.jpg"
    launch_script: "shadow_server_container.sh"
    desktop_icon_name: "1 - Launch Server Container"
    desktop_icon_path: "Shadow Advanced Launchers/1 - Launch Server Container"
    launch_terminal: "false"

- name: Install desktop icon for launching ROSCORE
  import_tasks: default-icon.yml
  vars:
    template: ../../../common/resources/templates/scripts/start-roscore.j2
    desktop_icon_png: "ROS_logo.png"
    launch_script: "shadow_roscore.sh"
    desktop_icon_name: "2 - Launch Server ROSCORE"
    desktop_icon_path: "Shadow Advanced Launchers/2 - Launch Server ROSCORE"
    launch_terminal: "false"

- name: Set default sim_biotacs to false if polhemus is being used (user can still override)
  set_fact:
    sim_biotacs: false
  when: glove=="polhemus"

- name: Install desktop icon for Teleop server Simulation (Unimanual Right HaptX)
  import_tasks: roslaunch-icon.yml
  vars:
    desktop_icon_png: "haptx_right.png"
    launch_script: "shadow_sim_right.sh"
    desktop_icon_name: "3 - Launch Right HaptX Teleop Simulation"
    desktop_icon_path: "Shadow Advanced Launchers/3 - Launch Right HaptX Teleop Simulation"
    project_name_input: "sr_teleop_vive_haptx"
    launch_file_input: "teleop_vive_haptx.launch sim:=true side:=right vive:={{ real_vive | lower }} biotacs:={{ sim_biotacs | lower }}"
  when: glove=="haptx"

- name: Install desktop icon for Teleop server Simulation (Unimanual Left HaptX)
  import_tasks: roslaunch-icon.yml
  vars:
    desktop_icon_png: "haptx_left.png"
    launch_script: "shadow_sim_left.sh"
    desktop_icon_name: "3 - Launch Left HaptX Teleop Simulation"
    desktop_icon_path: "Shadow Advanced Launchers/3 - Launch Left HaptX Teleop Simulation"
    project_name_input: "sr_teleop_vive_haptx"
    launch_file_input: "teleop_vive_haptx.launch sim:=true side:=left vive:={{ real_vive | lower }} biotacs:={{ sim_biotacs | lower }}"
  when: glove=="haptx"

- name: Install desktop icon for Teleop server Simulation (Bimanual HaptX)
  import_tasks: roslaunch-icon.yml
  vars:
    desktop_icon_png: "haptx_bimanual.png"
    launch_script: "shadow_sim_bimanual.sh"
    desktop_icon_name: "3 - Launch Bimanual HaptX Teleop Simulation"
    desktop_icon_path: "Shadow Advanced Launchers/3 - Launch Bimanual HaptX Teleop Simulation"
    project_name_input: "sr_teleop_vive_haptx"
    launch_file_input: "teleop_bimanual_vive_haptx.launch sim:=true vive:={{ real_vive | lower }} biotacs:={{ sim_biotacs | lower }}"
  when: glove=="haptx"

- name: Install desktop icon for Teleop server Simulation (Unimanual Right Polhemus)
  import_tasks: roslaunch-icon.yml
  vars:
    desktop_icon_png: "polhemus.png"
    launch_script: "shadow_sim_right.sh"
    desktop_icon_name: "3 - Launch Right Polhemus Teleop Simulation"
    desktop_icon_path: "Shadow Advanced Launchers/3 - Launch Right Polhemus Teleop Simulation"
    project_name_input: "sr_teleop_vive_polhemus"
    launch_file_input: "sr_teleop_vive_polhemus.launch sim:=true side:=right vive:={{ real_vive | lower }} biotacs:={{ sim_biotacs | lower }} polhemus:={{ real_glove | lower }} palm_device:=tracker tracker_id:=1"
  when: glove=="polhemus"

- name: Install desktop icon for Teleop server Simulation (Unimanual Left Polhemus)
  import_tasks: roslaunch-icon.yml
  vars:
    desktop_icon_png: "polhemus.png"
    launch_script: "shadow_sim_left.sh"
    desktop_icon_name: "3 - Launch Left Polhemus Teleop Simulation"
    desktop_icon_path: "Shadow Advanced Launchers/3 - Launch Left Polhemus Teleop Simulation"
    project_name_input: "sr_teleop_vive_polhemus"
    launch_file_input: "sr_teleop_vive_polhemus.launch sim:=true side:=left vive:={{ real_vive | lower }} biotacs:={{ sim_biotacs | lower }} polhemus:={{ real_glove | lower }} palm_device:=tracker tracker_id:=0"
  when: glove=="polhemus"

- name: Install desktop icon for Teleop server Simulation (Bimanual Polhemus)
  import_tasks: roslaunch-icon.yml
  vars:
    desktop_icon_png: "polhemus.png"
    launch_script: "shadow_sim_bimanual.sh"
    desktop_icon_name: "3 - Launch Bimanual Polhemus Teleop Simulation"
    desktop_icon_path: "Shadow Advanced Launchers/3 - Launch Bimanual Polhemus Teleop Simulation"
    project_name_input: "sr_teleop_vive_polhemus"
    launch_file_input: "sr_teleop_vive_polhemus.launch sim:=true vive:={{ real_vive | lower }} biotacs:={{ sim_biotacs | lower }} polhemus:={{ real_glove | lower }}"
  when: glove=="polhemus"

- name: Install desktop icon for running haptx mapping node right
  include_tasks: roslaunch-icon.yml
  vars:
    desktop_icon_png: "haptx_right.png"
    launch_script: "shadow_haptx_mapping_launch_right.sh"
    desktop_icon_name: "4 - Launch Right HaptX Mapping"
    desktop_icon_path: "Shadow Advanced Launchers/4 - Launch Right HaptX Mapping"
    project_name_input: "sr_teleop_vive_haptx"
    launch_file_input: "haptx_base.launch hand_side_prefix:=rh"
  when: glove=="haptx" and real_glove

- name: Install desktop icon for running haptx mapping node left
  include_tasks: roslaunch-icon.yml
  vars:
    desktop_icon_png: "haptx_left.png"
    launch_script: "shadow_haptx_mapping_launch_left.sh"
    desktop_icon_name: "4 - Launch Left HaptX Mapping"
    desktop_icon_path: "Shadow Advanced Launchers/4 - Launch Left HaptX Mapping"
    project_name_input: "sr_teleop_vive_haptx"
    launch_file_input: "haptx_base.launch hand_side_prefix:=lh"
  when: glove=="haptx" and real_glove

- name: Install desktop icon for running haptx mapping node bimanual
  include_tasks: roslaunch-icon.yml
  vars:
    desktop_icon_png: "haptx_bimanual.png"
    launch_script: "shadow_haptx_mapping_launch_bimanual.sh"
    desktop_icon_name: "4 - Launch Bimanual HaptX Mapping"
    desktop_icon_path: "Shadow Advanced Launchers/4 - Launch Bimanual HaptX Mapping"
    project_name_input: "sr_teleop_vive_haptx"
    launch_file_input: "haptx_base_bimanual.launch"
  when: glove=="haptx" and real_glove

- name: Install desktop icon for running polhemus mapping node right
  include_tasks: roslaunch-icon.yml
  vars:
    desktop_icon_png: "polhemus.png"
    launch_script: "shadow_polhemus_mapping_launch_right.sh"
    desktop_icon_name: "4 - Launch Right Polhemus Mapping"
    desktop_icon_path: "Shadow Advanced Launchers/4 - Launch Right Polhemus Mapping"
    project_name_input: "sr_fingertip_hand_teleop"
    launch_file_input: "sr_fingertip_hand_teleop.launch hand_side_prefix:=rh"
  when: glove=="polhemus" and real_glove

- name: Install desktop icon for running polhemus mapping node left
  include_tasks: roslaunch-icon.yml
  vars:
    desktop_icon_png: "polhemus.png"
    launch_script: "shadow_polhemus_mapping_launch_left.sh"
    desktop_icon_name: "4 - Launch Left Polhemus Mapping"
    desktop_icon_path: "Shadow Advanced Launchers/4 - Launch Left Polhemus Mapping"
    project_name_input: "sr_fingertip_hand_teleop"
    launch_file_input: "sr_fingertip_hand_teleop.launch hand_side_prefix:=lh"
  when: glove=="polhemus" and real_glove

- name: Install desktop icon for running polhemus mapping node bimanual
  include_tasks: roslaunch-icon.yml
  vars:
    desktop_icon_png: "polhemus.png"
    launch_script: "shadow_polhemus_mapping_launch_bimanual.sh"
    desktop_icon_name: "4 - Launch Bimanual Polhemus Mapping"
    desktop_icon_path: "Shadow Advanced Launchers/4 - Launch Bimanual Polhemus Mapping"
    project_name_input: "sr_fingertip_hand_teleop"
    launch_file_input: "sr_fingertip_hand_teleop.launch"
  when: glove=="polhemus" and real_glove

- name: Install desktop icon for running right polhemus driver
  include_tasks: roslaunch-icon.yml
  vars:
    desktop_icon_png: "polhemus.png"
    launch_script: "shadow_polhemus_driver_right.sh"
    desktop_icon_name: "5 - Launch Right Polhemus Driver"
    desktop_icon_path: "Shadow Advanced Launchers/5 - Launch Right Polhemus Driver"
    project_name_input: "sr_fingertip_hand_teleop"
    launch_file_input: "polhemus.launch"
  when: glove=="polhemus" and real_glove

- name: Install desktop icon for running left polhemus driver
  include_tasks: roslaunch-icon.yml
  vars:
    desktop_icon_png: "polhemus.png"
    launch_script: "shadow_polhemus_driver_left.sh"
    desktop_icon_name: "5 - Launch Left Polhemus Driver"
    desktop_icon_path: "Shadow Advanced Launchers/5 - Launch Left Polhemus Driver"
    project_name_input: "sr_fingertip_hand_teleop"
    launch_file_input: "polhemus.launch"
  when: glove=="polhemus" and real_glove

- name: Install desktop icon for running bimanual polhemus driver
  include_tasks: roslaunch-icon.yml
  vars:
    desktop_icon_png: "polhemus.png"
    launch_script: "shadow_polhemus_driver_bimanual.sh"
    desktop_icon_name: "5 - Launch Bimanual Polhemus Driver"
    desktop_icon_path: "Shadow Advanced Launchers/5 - Launch Bimanual Polhemus Driver"
    project_name_input: "sr_fingertip_hand_teleop"
    launch_file_input: "polhemus.launch"
  when: glove=="polhemus" and real_glove

- name: Set mock parameters based on glove=haptx
  set_fact:
    project_name_value: "sr_teleop_vive_haptx"
    launch_file_value: "teleop_mock.launch"
  when: glove=="haptx"

- name: Set mock parameters based on glove=polhemus
  set_fact:
    project_name_value: "sr_teleop_vive_polhemus"
    launch_file_value: "teleop_mock.launch"
  when: glove=="polhemus"

- name: Set mock parameters based on glove if glove is not haptx or polhemus
  set_fact:
    project_name_value: "sr_teleop_mock"
    launch_file_value: "sr_teleop_mock.launch"
  when: glove!="polhemus" and glove!="haptx"

- name: Install desktop icon for Launch Simulated Right Teleop Mock
  include_tasks: roslaunch-icon.yml
  vars:
    desktop_icon_png: "vive_tracker.jpg"
    launch_script: "shadow_mock_right.sh"
    desktop_icon_name: "6 - Launch Simulated Right Teleop Mock"
    desktop_icon_path: "Shadow Advanced Launchers/6 - Launch Simulated Right Teleop Mock"
    project_name_input: "{{ project_name_value }}"
    launch_file_input: "{{ launch_file_value }} bimanual:=false side:=right"
  when: not real_vive

- name: Install desktop icon for Launch Simulated Left Teleop Mock
  include_tasks: roslaunch-icon.yml
  vars:
    desktop_icon_png: "vive_tracker.jpg"
    launch_script: "shadow_mock_left.sh"
    desktop_icon_name: "6 - Launch Simulated Left Teleop Mock"
    desktop_icon_path: "Shadow Advanced Launchers/6 - Launch Simulated Left Teleop Mock"
    project_name_input: "{{ project_name_value }}"
    script_name_input: "{{ launch_file_value }} bimanual:=false side:=left"
  when: not real_vive

- name: Install desktop icon for Launch Simulated Bimanual Teleop Mock
  include_tasks: roslaunch-icon.yml
  vars:
    desktop_icon_png: "vive_tracker.jpg"
    launch_script: "shadow_mock_bimanual.sh"
    desktop_icon_name: "6 - Launch Simulated Bimanual Teleop Mock"
    desktop_icon_path: "Shadow Advanced Launchers/6 - Launch Simulated Bimanual Teleop Mock"
    project_name_input: "{{ project_name_value }}"
    script_name_input: "{{ launch_file_value }} bimanual:=true"
  when: not real_vive

- name: Include products/common/demo-icons role
  include_role:
    name: products/common/demo-icons
  vars:
    demo_icon_folder: "{{ user_folder }}/Desktop/Shadow Demos"
    bimanual: true
  when: demo_icons|bool
