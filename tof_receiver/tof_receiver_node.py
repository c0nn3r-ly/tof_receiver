#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32
import serial

class TofReceiverNode(Node):
    def __init__(self):
        super().__init__('tof_receiver_node')
        
        # 1. 声明串口号参数和波特率参数（可在 launch 或命令行动态修改）
        self.declare_parameter('port', '/dev/ttyUSB0')
        self.declare_parameter('baud', 115200)
        
        port = self.get_parameter('port').value
        baud = self.get_parameter('baud').value
        
        # 2. 声明 4 个标准的 ToF 绝对高度话题
        self.pub_tof1 = self.create_publisher(Int32, '/tof/leg1', 10)
        self.pub_tof2 = self.create_publisher(Int32, '/tof/leg2', 10)
        self.pub_tof3 = self.create_publisher(Int32, '/tof/leg3', 10)
        self.pub_tof4 = self.create_publisher(Int32, '/tof/leg4', 10)
        
        # 3. 尝试打开物理串口
        try:
            self.ser = serial.Serial(port, baud, timeout=1.0)
            self.get_logger().info(f" [TOF_RECEIVER] Connected to ESP32 on {port}!")
        except Exception as e:
            self.get_logger().error(f" [TOF_RECEIVER] Failed to open serial port: {e}")
            raise e
            
        # 4. 创建 10ms 周期定时器（100Hz 频率高频接收并转发）
        self.timer = self.create_timer(0.01, self.read_serial_loop)

    def read_serial_loop(self):
        if self.ser.in_waiting > 0:
            try:
                # 读取一行串口文本，例如 "120,450,1100,850"
                line = self.ser.readline().decode('utf-8').strip()
                
                self.get_logger().info(f"Raw Serial Data: '{line}'")
                
                parts = line.split(',')
                if len(parts) == 4:
                    val1 = int(parts[0])
                    val2 = int(parts[1])
                    val3 = int(parts[2])
                    val4 = int(parts[3])
                    
                    # 5. 发布为标准的 ROS 2 话题
                    self.pub_tof1.publish(Int32(data=val1))
                    self.pub_tof2.publish(Int32(data=val2))
                    self.pub_tof3.publish(Int32(data=val3))
                    self.pub_tof4.publish(Int32(data=val4))
            except Exception as e:
                pass

def main(args=None):
    rclpy.init(args=args)
    node = TofReceiverNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()