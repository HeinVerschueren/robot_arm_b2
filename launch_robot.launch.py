from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction, ExecuteProcess
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

    vision_node = Node(
        package='vision_node',
        executable='vision_node',
        name='vision_node',
        output='screen'
    )

    overige_nodes = TimerAction(
        period=8.0,
        actions=[
            robot_launch,
            ExecuteProcess(
                cmd=['python3', os.path.expanduser('~/Vision/robot_arm_b2/controller_code/controller.py')],
                output='screen'
            ),
            ExecuteProcess(
                cmd=['python3', os.path.expanduser('~/Vision/robot_arm_b2/controller_code/HMI.py')],
                output='screen'
            ),
            ExecuteProcess(
                cmd=['python3', os.path.expanduser('~/Vision/robot_arm_b2/manipulatorCodeB2.py')],
                output='screen'
            ),
        ]
    )

    return LaunchDescription([
        vision_node,
        overige_nodes
    ])
