import os
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_icons_in_docker(host):
    desktop_path = '/home/' + str(host.user().name) + '/Desktop/'
    script_path = '/home/' + str(host.user().name) + \
                  '/.shadow_launcher_app/shadow_hand_launcher/'
    icons = (
        'Teleop_control_machine_Launch_Demohand_A',
        'Teleop_control_machine_Launch_Demohand_B',
        'Teleop_control_machine_Launch_Demohand_C',
        'Teleop_Container_Launch',
        'Teleop_GUI',
        'Teleop_ROSCORE'
        )
    scripts = (
        'teleop_exec_A',
        'teleop_exec_B',
        'teleop_exec_C',
        'shadow_launcher_exec',
        'shadow_roslaunch_demo',
        'shadow_roscore'
        )
    for icon in icons:
        assert host.file(desktop_path+icon+'.desktop').exists
    for script in scripts:
        assert host.file(script_path+script+'.sh').exists
