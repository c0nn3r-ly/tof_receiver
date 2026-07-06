"""Launch 文件：启动 tof_receiver 节点，并支持透传 port / baud 参数。

用法：
  ros2 launch tof_receiver tof_receiver.launch.py
  ros2 launch tof_receiver tof_receiver.launch.py port:=/dev/ttyACM0 baud:=115200
"""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            'port',
            default_value='/dev/ttyUSB0',
            description='ESP32 串口设备节点',
        ),
        DeclareLaunchArgument(
            'baud',
            default_value='115200',
            description='串口波特率',
        ),
        Node(
            package='tof_receiver',
            executable='tof_receiver_node',
            name='tof_receiver_node',
            output='screen',
            parameters=[{
                'port': LaunchConfiguration('port'),
                'baud': LaunchConfiguration('baud'),
            }],
        ),
    ])
