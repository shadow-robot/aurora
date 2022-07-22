import os
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_hosts_file(host):
    f = host.file('/etc/hosts')

    assert f.exists
    assert f.user == 'root'
    assert f.group == 'root'


def test_docker_installed(host):
    package = host.package('docker-ce')
    assert package.is_installed


def test_icons_in_docker(host):
    hostuser = str(host.user().name)
    desktop_path = f'/home/{hostuser}/Desktop/'
    script_path = f'/home/{hostuser}/.shadow_launcher_app_teleop_shadow_glove/shadow_hand_launcher/'
    save_logs_script_path = f'/home/{hostuser}/.shadow_save_log_app/save_latest_ros_logs/'
    icons = (
        'Launch Shadow Right Teleop 8DOF',
        'Shadow NUC RQT',
        'Shadow Advanced Launchers/1 - Launch Server Container',
        'Shadow Advanced Launchers/2 - Launch Server ROSCORE',
        'Shadow Advanced Launchers/3 - Launch NUC Right Side Teleop Hardware Control Loop',
        'Shadow Advanced Launchers/3 - Demohand A Launch NUC Right Side Teleop Hardware Control Loop',
        'Shadow Advanced Launchers/3 - Demohand B Launch NUC Right Side Teleop Hardware Control Loop',
        'Shadow Advanced Launchers/3 - Demohand C Launch NUC Right Side Teleop Hardware Control Loop',
        'Shadow Advanced Launchers/3 - Demohand D Launch NUC Left Side Teleop Hardware Control Loop',
        'Shadow Advanced Launchers/4 - Launch Right Teleop GUI 8DOF',
        'Shadow Advanced Launchers/5 - Launch Right Shadow Glove Driver',
        'Shadow Advanced Launchers/6 - Launch Right Shadow Glove Mapping',
        'Shadow Advanced Launchers/Launch NUC Container',
        'Shadow Demos/Close Right Hand',
        'Shadow Demos/Open Right Hand',
        'Shadow ROS Logs Saver and Uploader',
        'Teleop Documentation',
        'Shadow Advanced Launchers/Launch Local Shadow Right Hand',
        'Shadow Advanced Launchers/Local Zero Force Mode - Right Hand',
        'Shadow Advanced Launchers/3 - Zero Force Mode - Right Hand',
        'Shadow System Monitor',
        'Steam Vive Binding',
        'Shadow Close Everything'
        )
    scripts = (
        'shadow_launch_right_teleop_8dof',
        'nuc_rqt',
        'shadow_server_container',
        'shadow_roscore',
        'shadow_nuc_right_hardware_control_loop',
        'teleop_exec_A',
        'teleop_exec_B',
        'teleop_exec_C',
        'teleop_exec_D',
        'shadow_GUI_right_8DOF',
        'shadow_glove_mapping_launch_right',
        'shadow_glove_driver_right',
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
    hand_manual_file = f"{desktop_path}Palm_EDC_User_Manual_1.7.pdf"
    assert host.file(hand_manual_file).exists
