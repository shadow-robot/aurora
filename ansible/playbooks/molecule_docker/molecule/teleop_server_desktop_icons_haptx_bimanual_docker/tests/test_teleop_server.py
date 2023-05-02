# Copyright 2022 Shadow Robot Company Ltd.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation version 2 of the License.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

import os
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_chrony_server_installed(host):
    file_path = "/etc/chrony/chrony.conf"
    assert host.file(file_path).exists


def test_udev_files(host):
    udev_path = '/etc/udev/rules.d/'

    udev_rules = (
        '60-HTC-Vive-perms-Ubuntu.rules',
        '99-steam-perms.rules',
        '90-VEC-USB-Footpedal.rules',
        '90-hazard-light.rules'
        )
    for udev_rule in udev_rules:
        assert host.file(udev_path + udev_rule).exists


def test_icons_in_docker(host):
    hostuser = str(host.user().name)
    desktop_path = f'/home/{hostuser}/Desktop/'
    script_path = f'/home/{hostuser}/.shadow_launcher_app_tactile_telerobot_system/shadow_hand_launcher/'
    save_logs_script_path = f'/home/{hostuser}/.shadow_save_log_app/save_latest_ros_logs/'
    icons = (
        'Launch Shadow Right Teleop',
        'Launch Shadow Left Teleop',
        'Launch Shadow Bimanual Teleop',
        'Shadow NUC RQT',
        'Shadow Advanced Launchers/Launch Server Container',
        'Right Side/1 - Launch Server Container',
        'Right Side/2 - Launch Server ROSCORE',
        'Left Side/1 - Launch Server Container',
        'Left Side/2 - Launch Server ROSCORE',
        'Bimanual/1 - Launch Server Container',
        'Bimanual/2 - Launch Server ROSCORE',
        'Right Side/3 - Launch NUC Right Side Teleop Hardware Control Loop',
        'Left Side/3 - Launch NUC Left Side Teleop Hardware Control Loop',
        'Bimanual/3 - Launch NUC Bimanual Teleop Hardware Control Loop',
        'Shadow Advanced Launchers/3 - Demohand A Launch NUC Right Side Teleop Hardware Control Loop',
        'Shadow Advanced Launchers/3 - Demohand B Launch NUC Right Side Teleop Hardware Control Loop',
        'Shadow Advanced Launchers/3 - Demohand C Launch NUC Right Side Teleop Hardware Control Loop',
        'Shadow Advanced Launchers/3 - Demohand D Launch NUC Left Side Teleop Hardware Control Loop',
        'Right Side/4 - Launch Right Teleop GUI',
        'Left Side/4 - Launch Left Teleop GUI',
        'Bimanual/4 - Launch Bimanual Teleop GUI',
        'Right Side/5 - Launch Right HaptX Mapping',
        'Left Side/5 - Launch Left HaptX Mapping',
        'Bimanual/5 - Launch Bimanual HaptX Mapping',
        'Shadow Advanced Launchers/Launch NUC Container',
        'Shadow Demos/Close Right Hand',
        'Shadow Demos/Open Right Hand',
        'Shadow Demos/Close Left Hand',
        'Shadow Demos/Open Left Hand',
        'Shadow Demos/Close Bimanual Hands',
        'Shadow Demos/Open Bimanual Hands',
        'Shadow ROS Logs Saver and Uploader',
        'Shadow Teleop Documentation',
        'Shadow System Monitor',
        'Local Launch/Launch Local Shadow Right Hand',
        'Local Launch/Launch Local Shadow Left Hand',
        'Local Launch/Launch Local Shadow Bimanual Hands',
        'Local Launch/Local Zero Force Mode - Left Hand',
        'Local Launch/Local Zero Force Mode - Right Hand',
        'Left Side/3 - Zero Force Mode - Left Hand',
        'Right Side/3 - Zero Force Mode - Right Hand',
        'Shadow Advanced Launchers/Bimanual Teleop Simulation',
        'Shadow Close Everything'
        )
    scripts = (
        'shadow_launch_right_teleop',
        'shadow_launch_left_teleop',
        'shadow_launch_bimanual_teleop',
        'nuc_rqt',
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
        'open_right_hand',
        'close_left_hand',
        'open_left_hand',
        'close_bimanual_hands',
        'open_bimanual_hands',
        'shadow_launcher_doc_exec',
        'shadow_launcher_system_monitor_exec',
        'shadow_local_right_launcher_exec',
        'shadow_local_left_launcher_exec',
        'shadow_local_bimanual_launcher_exec',
        'shadow_sim_demo_bimanual',
        'shadow_local_zero_force_mode_right',
        'shadow_local_zero_force_mode_left',
        'shadow_local_zero_force_mode_right_launcher',
        'shadow_local_zero_force_mode_left_launcher',
        'shadow_zero_force_mode_right',
        'shadow_zero_force_mode_left',
        'close_everything'
        )
    for icon in icons:
        assert host.file(f"{desktop_path}{icon}.desktop").exists

    for script in scripts:
        assert host.file(f"{script_path}{script}.sh").exists
    save_logs_file = f"{save_logs_script_path}save-latest-ros-logs.sh"
    assert host.file(save_logs_file).exists
