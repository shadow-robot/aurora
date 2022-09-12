import os
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_icons_in_docker(host):
    hostuser = str(host.user().name)
    desktop_path = f'/home/{hostuser}/Desktop/'
    script_path = f'/home/{hostuser}/.shadow_launcher_app_teleop_haptx/shadow_hand_launcher/'
    save_logs_script_path = f'/home/{hostuser}/.shadow_save_log_app/save_latest_ros_logs/'
    icons = (
        'Launch Shadow Right Teleop 8DOF Simulation',
        'Launch Shadow Left Teleop 8DOF Simulation',
        'Launch Shadow Bimanual Teleop 8DOF Simulation',
        'Shadow Advanced Launchers/Launch Server Container',
        'Right Side/1 - Launch Server Container',
        'Right Side/2 - Launch Server ROSCORE',
        'Left Side/1 - Launch Server Container',
        'Left Side/2 - Launch Server ROSCORE',
        'Bimanual/1 - Launch Server Container',
        'Bimanual/2 - Launch Server ROSCORE',
        'Right Side/3 - Launch Right Teleop Simulation 8DOF',
        'Left Side/3 - Launch Left Teleop Simulation 8DOF',
        'Bimanual/3 - Launch Bimanual Teleop Simulation 8DOF',
        'Right Side/4 - Launch Right HaptX Mapping',
        'Left Side/4 - Launch Left HaptX Mapping',
        'Bimanual/4 - Launch Bimanual HaptX Mapping',
        'Right Side/6 - Launch Simulated Right Teleop Mock',
        'Left Side/6 - Launch Simulated Left Teleop Mock',
        'Bimanual/6 - Launch Simulated Bimanual Teleop Mock',
        'Shadow Demos/Close Right Hand',
        'Shadow Demos/Open Right Hand',
        'Shadow Demos/Close Left Hand',
        'Shadow Demos/Open Left Hand',
        'Shadow ROS Logs Saver and Uploader',
        'Teleop Documentation',
        'Shadow System Monitor',
        'Shadow Close Everything'
        )
    scripts = (
        'shadow_launch_right_teleop_8dof_sim',
        'shadow_launch_left_teleop_8dof_sim',
        'shadow_launch_bimanual_teleop_8dof_sim',
        'shadow_server_container',
        'shadow_roscore',
        'shadow_sim_right_8DOF',
        'shadow_sim_left_8DOF',
        'shadow_sim_bimanual_8DOF',
        'shadow_haptx_mapping_launch_right',
        'shadow_haptx_mapping_launch_left',
        'shadow_haptx_mapping_launch_bimanual',
        'shadow_mock_right',
        'shadow_mock_left',
        'shadow_mock_bimanual',
        'close_right_hand',
        'open_right_hand',
        'close_left_hand',
        'open_left_hand',
        'shadow_launcher_doc_exec',
        'shadow_launcher_system_monitor_exec',
        'close_everything'
        )
    for icon in icons:
        assert host.file(f"{desktop_path}{icon}.desktop").exists

    for script in scripts:
        assert host.file(f"{script_path}{script}.sh").exists
    save_logs_file = f"{save_logs_script_path}save-latest-ros-logs.sh"
    assert host.file(save_logs_file).exists
    hand_manual_file = f"{desktop_path}Palm_EDC_User_Manual_1.7.pdf"
    assert host.file(hand_manual_file).exists
