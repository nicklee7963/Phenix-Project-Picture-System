import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import serial

class RailController(Node):
    def __init__(self):
        super().__init__('rail_controller')
        usb_port = '/dev/ttyUSB0' 
        baud_rate = 115200
        
        self.serial_connected = False
        try:
            self.serial_conn = serial.Serial(usb_port, baud_rate, timeout=1)
            self.serial_connected = True
            self.get_logger().info(f"✅ 成功連接 Arduino Nano 於 {usb_port}")
        except Exception as e:
            self.get_logger().error(f"❌ 序列埠連接失敗: {e} (測試模式運行中)")
            
        self.subscription = self.create_subscription(
            String,
            'rail_cmd',
            self.cmd_callback,
            10)

    def cmd_callback(self, msg):
        command = msg.data.lower()
        
        if not self.serial_connected:
            self.get_logger().warn(f"收到指令 [{command}]，但未連接 Arduino。")
            return

        # 寫入序列埠並同時印出 Log 讓你確認
        if command == 'up':
            self.serial_conn.write(b'U')
            self.get_logger().info("🔼 發送序列訊號: U (向上)")
        elif command == 'down':
            self.serial_conn.write(b'D')
            self.get_logger().info("🔽 發送序列訊號: D (向下)")
        elif command == 'stop':
            self.serial_conn.write(b'S')
            self.get_logger().info("⏹️ 發送序列訊號: S (停止)")

def main(args=None):
    rclpy.init(args=args)
    node = RailController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        if node.serial_connected:
            node.serial_conn.write(b'S')
            node.get_logger().info("接收到中斷訊號，已發送停止指令。")
    finally:
        node.destroy_node()
        # 加入 rclpy.ok() 判斷，避免重複 shutdown 報錯
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
