import os
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_icons_in_docker(host):
    hostuser = str(host.user().name)
    desktop_path = f'/home/{hostuser}/Desktop/'
    script_path = f'/home/{hostuser}/.shadow_launcher_app_teleop_shadow_glove/shadow_hand_launcher/'
    icons = (
        'Teleop_Container_Launch',
        )
    scripts = (
        'teleop_exec',
        )
    for icon in icons:
        assert host.file(f"{desktop_path}{icon}.desktop").exists
    for script in scripts:
        assert host.file(f"{script_path}{script}.sh").exists
