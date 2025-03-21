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

def find_files_by_extension_recursively(extension, host, current_dir=None, found_so_far=None):
    if found_so_far is None:
        found_files = []
    else:
        found_files = found_so_far
    for entry in host.file(current_dir).listdir():
        entry_path = f"{current_dir}/{entry}"
        entry_file = host.file(entry_path)
        if entry_file.is_file:
            if entry_path.endswith(extension):
                found_files.append(entry_path)
        elif entry_file.is_directory:
            find_files_by_extension_recursively(extension, host, entry_path, found_files)
        else:
            print(f"Debug: {entry_path} is neither a file nor a directory")
    return list(set(x.replace('//', '/') for x in found_files))

def check_things_exist(host, extension, path_to_test, things, type_of_thing='icon'):
    tested_thing_locations = []
    print(f"Testing if all known {type_of_thing} files were created")
    for thing in things:
        thing_location = f"{path_to_test}{thing}.{extension}"
        thing_exists = host.file(thing_location).exists
        if not thing_exists:
            print(f"Test if {type_of_thing} file exists: {thing_location} -- Failed :(")
        assert thing_exists
        tested_thing_locations.append(thing_location)
    print(f"Finding all {type_of_thing} files in {path_to_test}")
    found_thing_files = find_files_by_extension_recursively('desktop', host, path_to_test)
    print(f"Checking all {type_of_thing} files have a size greater than 0")
    for tested_thing_location in tested_thing_locations:
        assert host.file(tested_thing_location).size > 0
    print(f"Testing if we have any {type_of_thing} files not covered by this test")
    found_things_set = set(found_thing_files)
    tested_things_set = set(tested_thing_locations)
    things_not_tested_for = found_things_set - tested_things_set
    if len(things_not_tested_for) > 0:
        print(f"Uh oh - we have some unexpected {type_of_thing}s in the system. Please add these to this test file.")
        print(f"{type_of_thing}(s) not tested for:")
        for thing_not_tested_for in things_not_tested_for:
            print(f"  {thing_not_tested_for}")
    assert len(things_not_tested_for) == 0

def test_icons_in_docker(host):
    hostuser = str(host.user().name)
    script_path = f'/home/{hostuser}/.shadow_launcher_app_tactile_telerobot_system/shadow_hand_launcher/'
    desktop_path = f'/home/{hostuser}/.shadow_launcher_app_tactile_telerobot_system/Shadow Icons/'
    save_logs_script_path = f'/home/{hostuser}/.shadow_save_log_app/save_latest_ros_logs/'
    icons = (
        'Launch Shadow Right Teleop',
        'Launch Shadow Left Teleop',
        'Launch Shadow Bimanual Teleop',
        'Shadow NUC RQT',
        'Shadow Advanced Launchers/Launch Server Container',
        'Shadow Advanced Launchers/Right Side/1 - Launch Server Container',
        'Shadow Advanced Launchers/Right Side/2 - Launch Server ROSCORE',
        'Shadow Advanced Launchers/Left Side/1 - Launch Server Container',
        'Shadow Advanced Launchers/Left Side/2 - Launch Server ROSCORE',
        'Shadow Advanced Launchers/Bimanual/1 - Launch Server Container',
        'Shadow Advanced Launchers/Bimanual/2 - Launch Server ROSCORE',
        'Shadow Advanced Launchers/Right Side/3 - Launch NUC Right Side Teleop Hardware Control Loop',
        'Shadow Advanced Launchers/Left Side/3 - Launch NUC Left Side Teleop Hardware Control Loop',
        'Shadow Advanced Launchers/Bimanual/3 - Launch NUC Bimanual Teleop Hardware Control Loop',
        'Shadow Advanced Launchers/3 - Demohand A Launch NUC Right Side Teleop Hardware Control Loop',
        'Shadow Advanced Launchers/3 - Demohand B Launch NUC Right Side Teleop Hardware Control Loop',
        'Shadow Advanced Launchers/3 - Demohand C Launch NUC Right Side Teleop Hardware Control Loop',
        'Shadow Advanced Launchers/3 - Demohand D Launch NUC Left Side Teleop Hardware Control Loop',
        'Shadow Advanced Launchers/Right Side/4 - Launch Right Teleop GUI',
        'Shadow Advanced Launchers/Left Side/4 - Launch Left Teleop GUI',
        'Shadow Advanced Launchers/Bimanual/4 - Launch Bimanual Teleop GUI',
        'Shadow Advanced Launchers/Right Side/5 - Launch Right HaptX Mapping',
        'Shadow Advanced Launchers/Left Side/5 - Launch Left HaptX Mapping',
        'Shadow Advanced Launchers/Bimanual/5 - Launch Bimanual HaptX Mapping',
        'Shadow Advanced Launchers/Launch NUC Container',
        'Shadow Advanced Launchers/Left Teleop Simulation',
        'Shadow Advanced Launchers/Right Teleop Simulation',
        'Shadow Demos/Close Right Hand',
        'Shadow Demos/Open Right Hand',
        'Shadow Demos/Close Left Hand',
        'Shadow Demos/Open Left Hand',
        'Shadow Demos/Close Bimanual Hands',
        'Shadow Demos/Open Bimanual Hands',
        'Shadow Demos/Demo Bimanual Hands',
        'Shadow Demos/Demo Left Hand',
        'Shadow Demos/Demo Right Hand',
        'Shadow ROS Logs Saver and Uploader',
        'Shadow Teleop Documentation',
        'Shadow System Monitor',
        'Shadow Advanced Launchers/Local Launch/Launch Local Shadow Right Hand',
        'Shadow Advanced Launchers/Local Launch/Launch Local Shadow Left Hand',
        'Shadow Advanced Launchers/Local Launch/Launch Local Shadow Bimanual Hands',
        'Shadow Advanced Launchers/Local Launch/Local Zero Force Mode - Left Hand',
        'Shadow Advanced Launchers/Local Launch/Local Zero Force Mode - Right Hand',
        'Shadow Advanced Launchers/Left Side/3 - Zero Force Mode - Left Hand',
        'Shadow Advanced Launchers/Right Side/3 - Zero Force Mode - Right Hand',
        'Shadow Advanced Launchers/Bimanual Teleop Simulation',
        'Shadow Close Everything',
        'Tactile Telerobot System'
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
    check_things_exist(host=host, extension='desktop', path_to_test=desktop_path, things=icons, type_of_thing='icon')
    check_things_exist(host=host, extension='sh', path_to_test=script_path, things=scripts, type_of_thing='script')

    save_logs_file = f"{save_logs_script_path}save-latest-ros-logs.sh"
    assert host.file(save_logs_file).exists
    dolphin_icon = f"/home/{hostuser}/Desktop/Tactile Telerobot System.desktop"
    assert host.file(dolphin_icon).exists
