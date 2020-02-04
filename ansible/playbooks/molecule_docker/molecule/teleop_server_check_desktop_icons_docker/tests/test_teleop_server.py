import os
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_icons_in_docker(host):
    desktop_path = '/home/' + str(host.user().name) + '/Desktop/'
    script_path = '/home/' + str(host.user().name) + \
                  '/.shadow_launcher_app/shadow_hand_launcher/'
    save_logs_script_path = '/home/' + str(host.user().name) + \
                            '/.shadow_save_log_app/save_latest_ros_logs/'
    icons = (
        'Teleop_control_machine_Launch_Demohand_A',
        'Teleop_control_machine_Launch_Demohand_B',
        'Teleop_control_machine_Launch_Demohand_C',
        'Teleop_Container_Launch',
        'Teleop_GUI',
        'Teleop_ROSCORE',
        'Teleop_Simulation',
        'Teleop_Documentation',
        'Shadow ROS Logs Saver and Uploader'
        )
    scripts = (
        'teleop_exec_A',
        'teleop_exec_B',
        'teleop_exec_C',
        'shadow_launcher_exec',
        'shadow_roslaunch_demo',
        'shadow_roscore',
        'shadow_sim_demo',
        'shadow_launcher_doc_exec'
        )
    for icon in icons:
        assert host.file(desktop_path+icon+'.desktop').exists
    for script in scripts:
        assert host.file(script_path+script+'.sh').exists
    save_logs_file = save_logs_script_path+'save-latest-ros-logs.sh'
    assert host.file(save_logs_file).exists


def test_openvpn_server_files(host):
    openvpn_path = '/etc/openvpn/'

    openvpn_files = (
        'server.key',
        'server.crt',
        'ca.crt',
        'ta.key',
        'dh2048.pem'
        )
    for openvpn_file in openvpn_files:
        assert host.file(openvpn_path + openvpn_file).exists
    assert host.file(
        '/home/' + str(host.user().name) +
        '/openvpn-ca/teleop-client/teleop-client.ovpn').exists
