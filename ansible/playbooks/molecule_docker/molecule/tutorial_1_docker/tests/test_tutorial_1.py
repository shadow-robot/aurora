import os
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_icons_in_docker(host):
    desktop_path = '/home/' + str(host.user().name) + '/Desktop/'
    script_path = '/home/' + str(host.user().name) + \
                  '/.tutorial/tutorial_1/'
    script = "show_terminal"

    icon = "Launch_Tutorial_1"

    print(icon)
    print(desktop_path+icon+'.desktop')
    assert host.file(desktop_path+icon+'.desktop').exists
    assert host.file(script_path+script+'.sh').exists
