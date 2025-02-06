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


def test_hosts_file(host):
    host_file = host.file('/etc/hosts')

    assert host_file.exists
    assert host_file.user == 'root'
    assert host_file.group == 'root'


def test_docker_installed(host):
    package = host.package('docker-ce')
    assert package.is_installed

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
    script_path = f'/home/{hostuser}/.shadow_launcher_app_shadow_teleoperation_system/shadow_hand_launcher/'
    desktop_path = f'/home/{hostuser}/.shadow_launcher_app_shadow_teleoperation_system/Shadow Icons/'
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
        'Shadow Advanced Launchers/Launch Server Container',
        'Shadow Advanced Launchers/Right Teleop Simulation',
        'Shadow Advanced Launchers/Launch Shadow Right Glove Calibration',
        'Shadow Demos/Demo Right Hand',
        'Shadow Teleoperation System',
        'Shadow Demos/Close Right Hand',
        'Shadow Demos/Open Right Hand',
        'Shadow ROS Logs Saver and Uploader',
        'Shadow Teleop Documentation',
        'Shadow Advanced Launchers/Local Launch/Launch Local Shadow Right Hand',
        'Shadow Advanced Launchers/Local Launch/Local Zero Force Mode - Right Hand',
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
    check_things_exist(host=host, extension='desktop', path_to_test=desktop_path, things=icons, type_of_thing='icon')
    check_things_exist(host=host, extension='sh', path_to_test=script_path, things=scripts, type_of_thing='script')

    save_logs_file = f"{save_logs_script_path}save-latest-ros-logs.sh"
    assert host.file(save_logs_file).exists
    dolphin_icon = f"/home/{hostuser}/Desktop/Shadow Teleoperation System.desktop"
    assert host.file(dolphin_icon).exists
