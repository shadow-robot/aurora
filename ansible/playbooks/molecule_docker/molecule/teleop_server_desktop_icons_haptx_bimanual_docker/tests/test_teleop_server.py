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
        'Teleop_control_machine_Launch_bimanual_demohands_B_D',
        'Teleop_Container_Launch',
        'Teleop_GUI_haptx',
        'Teleop_ROSCORE',
        'ROS_Logs_Saver',
        'Teleop_Haptx_Mapping_Launch'
        )
    scripts = (
        'teleop_exec_bimanual',
        'shadow_launcher_exec',
        'shadow_roslaunch_demo',
        'shadow_roscore',
        'shadow_haptx_mapping_launch_demo'
        )
    for icon in icons:
        assert host.file(desktop_path+icon+'.desktop').exists
    for script in scripts:
        assert host.file(script_path+script+'.sh').exists
    save_logs_file = save_logs_script_path+'save-latest-ros-logs.sh'
    assert host.file(save_logs_file).exists
