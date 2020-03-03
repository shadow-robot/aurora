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
        'Launch Shadow Right Teleop',
        'Shadow NUC RQT',
        'Shadow Advanced Launchers/1 - Launch Server Container',
        'Shadow Advanced Launchers/2 - Launch Server ROSCORE',
        'Shadow Advanced Launchers/3 - Launch NUC Right ' +
        'Side Teleop Hardware Control Loop',
        'Shadow Advanced Launchers/3 - Demohand A Launch NUC ' +
        'Right Side Teleop Hardware Control Loop',
        'Shadow Advanced Launchers/3 - Demohand B Launch NUC ' +
        'Right Side Teleop Hardware Control Loop',
        'Shadow Advanced Launchers/3 - Demohand C Launch NUC ' +
        'Right Side Teleop Hardware Control Loop',
        'Shadow Advanced Launchers/3 - Demohand D Launch NUC ' +
        'Right Side Teleop Hardware Control Loop',
        'Shadow Advanced Launchers/4 - Launch Right Teleop GUI',
        'Shadow Advanced Launchers/5 - Launch Right Polhemus Mapping',
        'Shadow Advanced Launchers/6 - Launch Right Polhemus Driver',
        'Shadow Advanced Launchers/Launch NUC Container',
        'Shadow Demos/Close Right Hand',
        'Shadow Demos/Demo Right Hand',
        'Shadow Demos/Open Right Hand',
        'Shadow ROS Logs Saver',
        'Teleop Documentation',
        )
    scripts = (   
        'shadow_launch_right_teleop.sh',
        'nuc_rqt',
        'shadow_server_container',
        'shadow_roscore',
        'shadow_nuc_right_hardware_control_loop',
        'teleop_exec_A',
        'teleop_exec_B',
        'teleop_exec_C',
        'teleop_exec_D',   
        'shadow_GUI_right',
        'shadow_polhemus_mapping_launch_right.sh',
        'shadow_polhemus_driver_right.sh',
        'shadow_nuc_container',
        'close_right_hand',
        'demo_right_hand',
        'open_right_hand',
        'shadow_launcher_doc_exec.sh',
        'shadow_sim_demo.sh'
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
