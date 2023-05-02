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


def test_icons_in_docker(host):
    hostuser = str(host.user().name)
    desktop_path = f'/home/{hostuser}/Desktop/'
    script_path = f'/home/{hostuser}/.shadow_launcher_app_tactile_telerobot_system/shadow_hand_launcher/'
    save_logs_script_path = f'/home/{hostuser}/.shadow_save_log_app/save_latest_ros_logs/'
    icons = (
        'Launch Shadow Right Teleop Simulation',
        'Launch Shadow Left Teleop Simulation',
        'Launch Shadow Bimanual Teleop Simulation',
        'Shadow Advanced Launchers/Launch Server Container',
        'Right Side/1 - Launch Server Container',
        'Right Side/2 - Launch Server ROSCORE',
        'Left Side/1 - Launch Server Container',
        'Left Side/2 - Launch Server ROSCORE',
        'Bimanual/1 - Launch Server Container',
        'Bimanual/2 - Launch Server ROSCORE',
        'Right Side/3 - Launch Right Teleop Simulation',
        'Left Side/3 - Launch Left Teleop Simulation',
        'Bimanual/3 - Launch Bimanual Teleop Simulation',
        'Right Side/4 - Launch Right HaptX Mapping',
        'Left Side/4 - Launch Left HaptX Mapping',
        'Bimanual/4 - Launch Bimanual HaptX Mapping',
        'Right Side/6 - Launch Simulated Right Teleop Mock',
        'Left Side/6 - Launch Simulated Left Teleop Mock',
        'Bimanual/6 - Launch Simulated Bimanual Teleop Mock',
        'Shadow Demos/Close Right Hand',
        'Shadow Demos/Open Right Hand',
        'Shadow Demos/Close Left Hand',
        'Shadow Demos/Open Left Hand',
        'Shadow ROS Logs Saver and Uploader',
        'Shadow Teleop Documentation',
        'Shadow System Monitor',
        'Shadow Close Everything'
        )
    scripts = (
        'shadow_launch_right_teleop_sim',
        'shadow_launch_left_teleop_sim',
        'shadow_launch_bimanual_teleop_sim',
        'shadow_server_container',
        'shadow_roscore',
        'shadow_sim_right',
        'shadow_sim_left',
        'shadow_sim_bimanual',
        'shadow_haptx_mapping_launch_right',
        'shadow_haptx_mapping_launch_left',
        'shadow_haptx_mapping_launch_bimanual',
        'shadow_mock_right',
        'shadow_mock_left',
        'shadow_mock_bimanual',
        'close_right_hand',
        'open_right_hand',
        'close_left_hand',
        'open_left_hand',
        'shadow_launcher_doc_exec',
        'shadow_launcher_system_monitor_exec',
        'close_everything'
        )
    for icon in icons:
        assert host.file(f"{desktop_path}{icon}.desktop").exists

    for script in scripts:
        assert host.file(f"{script_path}{script}.sh").exists
    save_logs_file = f"{save_logs_script_path}save-latest-ros-logs.sh"
    assert host.file(save_logs_file).exists
