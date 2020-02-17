import os
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_chrony_server_installed(host):
    file_path = "/etc/chrony/chrony.conf"
    assert host.file(file_path).exists


def test_icons_in_docker(host):
    desktop_path = '/home/' + str(host.user().name) + '/Desktop/'
    script_path = '/home/' + str(host.user().name) + \
                  '/.shadow_launcher_app/shadow_hand_launcher/'
    save_logs_script_path = '/home/' + str(host.user().name) + \
                            '/.shadow_save_log_app/save_latest_ros_logs/'
    icons = (
        'Launch Shadow Right Hand',
        'Launch Shadow Left Hand',
        'Launch Shadow Bimanual Hands',
        'Shadow NUC RQT',
        'Shadow Advanced Launchers/1 - Launch Server Container',
        'Shadow Advanced Launchers/2 - Launch Server ROSCORE',
        'Shadow Advanced Launchers/3 - Launch NUC Container ' +
        'and Right Hand Hardware Control Loop',
        'Shadow Advanced Launchers/3 - Launch NUC Container ' +
        'and Left Hand Hardware Control Loop',
        'Shadow Advanced Launchers/3 - Launch NUC Container ' +
        'and Bimanual Hands Hardware Control Loop',
        'Shadow Advanced Launchers/4 - Launch Server Unimanual GUI',
        'Shadow Advanced Launchers/4 - Launch Server Bimanual GUI',
        'Shadow Advanced Launchers/Launch NUC Container',
        'Shadow Demos/Close Right Hand',
        'Shadow Demos/Demo Right Hand',
        'Shadow Demos/Open Right Hand',
        'Shadow Demos/Close Left Hand',
        'Shadow Demos/Demo Left Hand',
        'Shadow Demos/Open Left Hand',
        'Shadow Advanced Launchers/Launch Local Shadow Right Hand',
        'Shadow Advanced Launchers/Launch Local Shadow Left Hand',
        'Shadow Advanced Launchers/Launch Local Shadow Bimanual Hands',
        'Shadow ROS Logs Saver'
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
        'shadow_GUI_unimanual',
        'shadow_GUI_bimanual',
        'shadow_nuc_container',
        'close_right_hand',
        'demo_right_hand',
        'open_right_hand',
        'close_left_hand',
        'demo_left_hand',
        'open_left_hand',
        'shadow_local_right_launcher_exec',
        'shadow_local_left_launcher_exec',
        'shadow_local_bimanual_launcher_exec'
        )
    for icon in icons:
        assert host.file(desktop_path+icon+'.desktop').exists
    for script in scripts:
        assert host.file(script_path+script+'.sh').exists
    save_logs_file = save_logs_script_path+'save-latest-ros-logs.sh'
    assert host.file(save_logs_file).exists
