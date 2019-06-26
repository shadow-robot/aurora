import os
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_udev_files(host):
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
    assert host.file('/home/user/openvpn-ca/teleop-client/teleop-client.ovpn').exists
