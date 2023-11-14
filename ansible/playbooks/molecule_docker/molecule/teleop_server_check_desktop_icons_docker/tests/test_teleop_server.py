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


def test_hosts_file(host):
    host_file = host.file('/etc/hosts')

    assert host_file.exists
    assert host_file.user == 'root'
    assert host_file.group == 'root'


def test_docker_installed(host):
    package = host.package('docker-ce')
    assert package.is_installed


def test_icons_in_docker(host):
    hostuser = str(host.user().name)
    desktop_path = f'/home/{hostuser}/Desktop/'
    script_path = f'/home/{hostuser}/.shadow_launcher_app_shadow_teleoperation_system/shadow_hand_launcher/'
    save_logs_script_path = f'/home/{hostuser}/.shadow_save_log_app/save_latest_ros_logs/'
    icons = (
        'Launch Shadow Right Teleop',
        'Shadow NUC RQT',
        'Shadow Advanced Launchers/1 - Launch Server Container',
        'Shadow Advanced Launchers/2 - Launch Server ROSCORE',
        'Shadow Advanced Launchers/3 - Launch NUC Right Side Teleop Hardware Control Loop',
        'Shadow Advanced Launchers/3 - Demohand A Launch NUC Right Side Teleop Hardware Control Loop',
        'Shadow Advanced Launchers/3 - Demohand B Launch NUC Right Side Teleop Hardware Control Loop',
        'Shadow Advanced Launchers/3 - Demohand C Launch NUC Right Side Teleop Hardware Control Loop',
        'Shadow Advanced Launchers/3 - Demohand D Launch NUC Left Side Teleop Hardware Control Loop',
        'Shadow Advanced Launchers/4 - Launch Right Teleop GUI',
        'Shadow Advanced Launchers/Launch NUC Container',
        'Shadow Demos/Close Right Hand',
        'Shadow Demos/Open Right Hand',
        'Shadow ROS Logs Saver and Uploader',
        'Shadow Teleop Documentation',
        'Local Launch/Launch Local Shadow Right Hand',
        'Local Launch/Local Zero Force Mode - Right Hand',
        'Shadow Advanced Launchers/3 - Zero Force Mode - Right Hand',
        'Shadow System Monitor',
        'Steam Vive Binding',
        'Shadow Close Everything'
        )
    scripts = (
        'shadow_launch_right_teleop',
        'nuc_rqt',
        'shadow_server_container',
        'shadow_roscore',
        'shadow_nuc_right_hardware_control_loop',
        'teleop_exec_A',
        'teleop_exec_B',
        'teleop_exec_C',
        'teleop_exec_D',
        'shadow_GUI_right',
        'shadow_nuc_container',
        'close_right_hand',
        'open_right_hand',
        'shadow_launcher_doc_exec',
        'shadow_launcher_system_monitor_exec',
        'shadow_local_right_launcher_exec',
        'shadow_sim_demo_right',
        'shadow_local_zero_force_mode_right',
        'shadow_local_zero_force_mode_right_launcher',
        'shadow_zero_force_mode_right',
        'close_everything'
        )
    for icon in icons:
        assert host.file(f"{desktop_path}{icon}.desktop").exists

    for script in scripts:
        assert host.file(f"{script_path}{script}.sh").exists
    save_logs_file = f"{save_logs_script_path}save-latest-ros-logs.sh"
    assert host.file(save_logs_file).exists
