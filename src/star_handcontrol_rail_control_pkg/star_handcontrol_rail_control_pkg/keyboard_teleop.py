import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import sys
import termios
import tty
import select

class KeyboardTeleop(Node):
    def __init__(self):
        super().__init__('keyboard_teleop')
        self.publisher_ = self.create_publisher(String, 'rail_cmd', 10)
        self.get_logger().info("滑軌鍵盤控制已啟動！")
        self.get_logger().info("👉 請「長按」 'w' 向上移動，或 's' 向下移動")
        self.get_logger().info("👉 放開按鍵自動停止，按下 Ctrl+C 退出")

def get_key(settings, timeout):
    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], timeout)
    if rlist:
        key = sys.stdin.read(1)
    else:
        key = ''
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

def main(args=None):
    rclpy.init(args=args)
    node = KeyboardTeleop()
    settings = termios.tcgetattr(sys.stdin)
    
    last_cmd = 'stop'
    try:
        # 使用迴圈持續監聽，取代原本的定時器
        while rclpy.ok():
            key = get_key(settings, 0.1) # 0.1秒 Timeout
            msg = String()
            
            if key == 'w':
                msg.data = 'up'
            elif key == 's':
                msg.data = 'down'
            elif key == '\x03': # 偵測到 Ctrl+C
                break
            else:
                msg.data = 'stop'
            
            if msg.data != last_cmd:
                node.publisher_.publish(msg)
                if msg.data == 'stop':
                    node.get_logger().info("放開按鍵，發送指令: 停止")
                else:
                    direction = "向上" if msg.data == 'up' else "向下"
                    node.get_logger().info(f"按鍵觸發，發送指令: {direction}")
                last_cmd = msg.data
                
            # 讓 ROS 2 處理內部事件
            rclpy.spin_once(node, timeout_sec=0)

    except Exception as e:
        node.get_logger().error(f"發生錯誤: {e}")
    finally:
        # 確保關閉時發送停止指令並恢復鍵盤設定
        msg = String()
        msg.data = 'stop'
        node.publisher_.publish(msg)
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
