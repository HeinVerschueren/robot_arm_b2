from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os
import glob

def find_esp32_port():
    """Auto-detect the ESP32 serial port."""
    # Check ACM ports first (ESP32-C3 native USB)
    acm_ports = sorted(glob.glob('/dev/ttyACM*'))
    if acm_ports:
        return acm_ports[0]
    # Fall back to USB serial ports
    usb_ports = sorted(glob.glob('/dev/ttyUSB*'))
    if usb_ports:
        return usb_ports[0]
    # Default fallback
    return '/dev/ttyACM0'

def generate_launch_description():
    esp32_port = find_esp32_port()

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

    # micro-ROS agent — bridges ESP32 voice recognition to ROS2
    microros_agent = ExecuteProcess(
        cmd=[
            'ros2', 'run', 'micro_ros_agent', 'micro_ros_agent',
            'serial', '--dev', esp32_port, '-b', '115200'
        ],
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
        microros_agent,
        overige_nodes
    ])
