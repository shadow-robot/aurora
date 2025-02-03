# Copyright 2022, 2024, 2025 Shadow Robot Company Ltd.
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
    desktop_path = f'/home/{hostuser}/.shadow_launcher_app_tactile_telerobot_system/Shadow Icons/'
    script_path = f'/home/{hostuser}/.shadow_launcher_app_tactile_telerobot_system/shadow_hand_launcher/'
    save_logs_script_path = f'/home/{hostuser}/.shadow_save_log_app/save_latest_ros_logs/'
    icons = (
        'Launch Shadow Right Teleop Simulation',
        'Launch Shadow Left Teleop Simulation',
        'Launch Shadow Bimanual Teleop Simulation',
        'Shadow Advanced Launchers/Launch Server Container',
        'Shadow Advanced Launchers/Right Side/1 - Launch Server Container',
        'Shadow Advanced Launchers/Right Side/2 - Launch Server ROSCORE',
        'Shadow Advanced Launchers/Left Side/1 - Launch Server Container',
        'Shadow Advanced Launchers/Left Side/2 - Launch Server ROSCORE',
        'Shadow Advanced Launchers/Bimanual/1 - Launch Server Container',
        'Shadow Advanced Launchers/Bimanual/2 - Launch Server ROSCORE',
        'Shadow Advanced Launchers/Right Side/3 - Launch Right Teleop Simulation',
        'Shadow Advanced Launchers/Left Side/3 - Launch Left Teleop Simulation',
        'Shadow Advanced Launchers/Bimanual/3 - Launch Bimanual Teleop Simulation',
        'Shadow Advanced Launchers/Right Side/4 - Launch Right HaptX Mapping',
        'Shadow Advanced Launchers/Left Side/4 - Launch Left HaptX Mapping',
        'Shadow Advanced Launchers/Bimanual/4 - Launch Bimanual HaptX Mapping',
        'Shadow Advanced Launchers/Right Side/6 - Launch Simulated Right Teleop Mock',
        'Shadow Advanced Launchers/Left Side/6 - Launch Simulated Left Teleop Mock',
        'Shadow Advanced Launchers/Bimanual/6 - Launch Simulated Bimanual Teleop Mock',
        'Shadow Demos/Close Bimanual Hands.desktop',
        'Shadow Demos/Close Left Hand.desktop',
        'Shadow Demos/Close Right Hand.desktop',
        'Shadow Demos/Demo Bimanual Hands.desktop',
        'Shadow Demos/Demo Left Hand.desktop',
        'Shadow Demos/Demo Right Hand.desktop',
        'Shadow Demos/Open Bimanual Hands.desktop',
        'Shadow Demos/Open Left Hand.desktop',
        'Shadow Demos/Open Right Hand.desktop',
        'Shadow ROS Logs Saver and Uploader',
        'Shadow Teleop Documentation',
        'Shadow System Monitor',
        'Shadow Close Everything',
        'Tactile Telerobot System'
        )
    scripts = (
        'close_bimanual_hands',
        'close_everything',
        'close_left_hand',
        'close_right_hand',
        'demo_bimanual_hands',
        'demo_left_hand',
        'demo_right_hand',
        'open_bimanual_hands',
        'open_left_hand',
        'open_right_hand',
        'shadow_haptx_mapping_launch_bimanual',
        'shadow_haptx_mapping_launch_left',
        'shadow_haptx_mapping_launch_right',
        'shadow_launch_bimanual_teleop_sim',
        'shadow_launch_left_teleop_sim',
        'shadow_launch_right_teleop_sim',
        'shadow_launcher_doc_exec',
        'shadow_launcher_system_monitor_exec',
        'shadow_mock_bimanual',
        'shadow_mock_left',
        'shadow_mock_right',
        'shadow_roscore',
        'shadow_server_container',
        'shadow_sim_bimanual',
        'shadow_sim_left',
        'shadow_sim_right',
        'shadowlogo.png',
        'teleop-server-setup',

        )
    for icon in icons:
        icon_location = f"{desktop_path}{icon}.desktop"
        icon_exists = host.file(icon_location).exists
        print(f"Testing icon exists: {icon_location}", end='')
        if icon_exists:
            print(" -- Passed!")
        else:
            print(" -- Failed :(")
        assert icon_exists

    for script in scripts:
        script_location = f"{script_path}{script}.sh"
        script_exists = host.file(script_location).exists
        print(f"Testing script exists: {script_location}", end='')
        if script_exists:
            print(" -- Passed!")
        else:
            print(" -- Failed :(")
        assert script_exists
    save_logs_file = f"{save_logs_script_path}save-latest-ros-logs.sh"
    assert host.file(save_logs_file).exists
    dolphin_icon = f"/home/{hostuser}/Desktop/Tactile Telerobot System.desktop'
    assert host.file(dolphin_icon).exists
