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


def test_icons_in_docker(host):
    hostuser = str(host.user().name)
    desktop_path = f'/home/{hostuser}/Desktop/'
    script_path = f'/home/{hostuser}/.shadow_launcher_app_dexterous_hand/shadow_hand_launcher/'
    save_logs_script_path = f'/home/{hostuser}/.shadow_save_log_app/save_latest_ros_logs/'
    icons = (
        'Launch Shadow Right Hand',
        'Launch Shadow Left Hand',
        'Launch Shadow Bimanual Hands',
        'Shadow NUC RQT',
        'Shadow Advanced Launchers/Launch Server Container',
        'Right Side/1 - Launch Server Container',
        'Right Side/2 - Launch Server ROSCORE',
        'Left Side/1 - Launch Server Container',
        'Left Side/2 - Launch Server ROSCORE',
        'Bimanual/1 - Launch Server Container',
        'Bimanual/2 - Launch Server ROSCORE',
        'Right Side/3 - Launch NUC Container and Right Hand Hardware Control Loop',
        'Left Side/3 - Launch NUC Container and Left Hand Hardware Control Loop',
        'Bimanual/3 - Launch NUC Container and Bimanual Hands Hardware Control Loop',
        'Left Side/3 - Zero Force Mode - Left Hand',
        'Right Side/3 - Zero Force Mode - Right Hand',
        'Local Launch/Local Zero Force Mode - Left Hand',
        'Local Launch/Local Zero Force Mode - Right Hand',
        'Left Side/4 - Launch Server Left Hand GUI',
        'Right Side/4 - Launch Server Right Hand GUI',
        'Bimanual/4 - Launch Server Bimanual GUI',
        'Shadow Advanced Launchers/Launch NUC Container',
        'Shadow Demos/Close Right Hand',
        'Shadow Demos/Demo Right Hand',
        'Shadow Demos/Open Right Hand',
        'Shadow Demos/Close Left Hand',
        'Shadow Demos/Open Left Hand',
        'Shadow Demos/Demo Left Hand',
        'Shadow Demos/Close Bimanual Hands',
        'Shadow Demos/Open Bimanual Hands',
        'Shadow Demos/Demo Bimanual Hands',
        'Local Launch/Launch Local Shadow Right Hand',
        'Local Launch/Launch Local Shadow Left Hand',
        'Local Launch/Launch Local Shadow Bimanual Hands',
        'Shadow ROS Logs Saver and Uploader',
        'Shadow Close Everything'
        )
    scripts = (
        'shadow_launch_everything_right',
        'shadow_launch_everything_left',
        'shadow_launch_everything_bimanual',
        'nuc_rqt',
        'shadow_server_container',
        'shadow_roscore',
        'shadow_nuc_right_hardware_control_loop',
        'shadow_nuc_left_hardware_control_loop',
        'shadow_nuc_bimanual_hardware_control_loop',
        'shadow_GUI_left',
        'shadow_GUI_right',
        'shadow_GUI_bimanual',
        'shadow_nuc_container',
        'close_right_hand',
        'open_right_hand',
        'demo_right_hand',
        'close_left_hand',
        'open_left_hand',
        'demo_left_hand',
        'close_bimanual_hands',
        'open_bimanual_hands',
        'demo_bimanual_hands',
        'shadow_local_right_launcher_exec',
        'shadow_local_left_launcher_exec',
        'shadow_local_bimanual_launcher_exec',
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
