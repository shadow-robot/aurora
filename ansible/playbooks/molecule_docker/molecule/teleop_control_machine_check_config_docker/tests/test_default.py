# Copyright 2022 Shadow Robot Company Ltd.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation version 2 of the License.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

import os
import testinfra.utils.ansible_runner
import docker

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_hosts_file(host):
    host_file = host.file('/etc/hosts')

    assert host_file.exists
    assert host_file.user == 'root'
    assert host_file.group == 'root'


def test_docker_installed(host):
    package = host.package('docker-ce')
    assert package.is_installed


def test_docker_container_exists(host):
    client = docker.from_env()
    try:
        client.containers.get('teleop')
        assert True
    except docker.errors.NotFound:
        assert False
    except docker.errors.APIError:
        assert False


def test_correct_docker_image(host):
    client = docker.from_env()
    image = str(client.containers.get('teleop').image)
    assert image == "<Image: 'public.ecr.aws/shadowrobot/dexterous-hand:noetic-release'>"


def test_sr_hand_config_exists_in_docker(host):
    client = docker.from_env()
    container = client.containers.get('teleop')
    path = '/home/user/projects/shadow_robot/base_deps/src/sr_hand_config'
    bits, stat = container.get_archive(path)
    assert stat['size'] > 0
    assert image == "<Image: 'public.ecr.aws/shadowrobot/" \
        "dexterous-hand:noetic-release'>"
