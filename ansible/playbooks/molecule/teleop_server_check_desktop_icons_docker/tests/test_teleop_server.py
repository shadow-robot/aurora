import os
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')

def test_icons_in_docker(host):
    user = host.user().name
    icon_list = []
    script_list = []
    script_path = '/home/'+str(user)+'/Desktop/'
    desktop_path = '/home/'+str(user) + \
                        '/.shadow_launcher_app/shadow_hand_launcher/'
    icon_list.append(desktop_path +
                     'Teleop_Control_Machine_Launch_Demohand_A.desktop')
    icon_list.append(desktop_path +
                     'Teleop_Control_Machine_Launch_Demohand_B.desktop')
    icon_list.append(desktop_path +
                     'Teleop_Control_Machine_Launch_Demohand_C.desktop')
    icon_list.append(desktop_path+'Teleop_Container_Launch.desktop')
    icon_list.append(desktop_path+'Teleop_GUI.desktop')
    icon_list.append(desktop_path+'Teleop_ROSCORE.desktop')

    script_list.append(script_path+'teleop_exec_A.sh')
    script_list.append(script_path+'teleop_exec_B.sh')
    script_list.append(script_path+'teleop_exec_C.sh')
    script_list.append(script_path+'shadow_launcher_exec.sh')
    script_list.append(script_path+'shadow_roslaunch_demo.sh')
    script_list.append(script_path+'shadow_roscore.sh')

    for icon in icon_list:
        assert host.file(icon).exists
    for script in script_list:
        assert host.file(script).exists
