import os
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_chrony_server_installed(host):
    file_path = "/etc/chrony/chrony.conf"
    assert host.file(file_path).exists


def test_udev_files(host):
    udev_path = '/lib/udev/rules.d/'

    udev_rules = (
        '60-HTC-Vive-perms-Ubuntu.rules',
        '99-steam-perms.rules'
        )
    for udev_rule in udev_rules:
        assert host.file(udev_path + udev_rule).exists


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
        'Shadow Advanced Launchers/Launch Local Shadow Right Hand',
        'Shadow Advanced Launchers/Launch Local Shadow Left Hand',
        'Shadow Advanced Launchers/Launch Local Shadow Bimanual Hands',
        'Shadow Advanced Launchers/3 - Zero Force Mode - Left Hand',
        'Shadow Advanced Launchers/3 - Zero Force Mode - Right Hand',
        'Shadow Advanced Launchers/Local Zero Force Mode - Left Hand',
        'Shadow Advanced Launchers/Local Zero Force Mode - Right Hand',
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
        'demo_right_hand',
        'open_right_hand',
        'close_left_hand',
        'demo_left_hand',
        'open_left_hand',
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
        assert host.file(desktop_path+icon+'.desktop').exists
    for script in scripts:
        assert host.file(script_path+script+'.sh').exists
    save_logs_file = save_logs_script_path+'save-latest-ros-logs.sh'
    assert host.file(save_logs_file).exists
    hand_manual_file = desktop_path+'Palm_EDC_User_Manual_1.7.pdf'
    assert host.file(hand_manual_file).exists
