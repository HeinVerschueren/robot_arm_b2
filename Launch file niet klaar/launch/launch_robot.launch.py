from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():

    robot_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('my_uf_bringup'),
                'launch',
                'real_robot.launch.py'
            )
        ),
        launch_arguments={'robot_ip': '192.168.1.164'}.items()
    )

    return LaunchDescription([
        robot_launch,

        Node(
            package='testfile',
            executable='controller',
            name='controller',
            output='screen'
        ),
        Node(
            package='testfile',
            executable='HMI',
            name='HMI',
            output='screen'
        ),
        Node(
            package='testfile',
            executable='vision_node',
            name='vision_node',
            output='screen'
        ),
        Node(
            package='testfile',
            executable='manipulatorCodeB2',
            name='manipulatorCodeB2',
            output='screen'
        ),
    ])