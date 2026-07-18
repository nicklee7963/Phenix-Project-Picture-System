import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image

class TimerCameraNode(Node):
    def __init__(self):
        super().__init__('timer_camera_node')
        
        # 1. 訂閱原本 camera_node 產生的連續影像 (假設 topic 為 /image_raw)
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.listener_callback,
            10)
            
        # 2. 建立新的發布者，負責傳送每 5 秒的照片到 WSL (Topic 為 /image_5sec)
        self.publisher_ = self.create_publisher(Image, '/image_5sec', 10)
        
        # 3. 設定計時器，每 5.0 秒執行一次
        self.timer = self.create_timer(5.0, self.timer_callback)
        
        self.latest_msg = None
        self.get_logger().info('五秒拍照節點已啟動，等待影像輸入...')

    def listener_callback(self, msg):
        # 隨時將最新的畫面暫存起來
        self.latest_msg = msg

    def timer_callback(self):
        # 每 5 秒觸發一次，如果有畫面就發布出去
        if self.latest_msg is not None:
            self.publisher_.publish(self.latest_msg)
            self.get_logger().info('已擷取畫面，並透過 Tailscale 發送！')

def main(args=None):
    rclpy.init(args=args)
    node = TimerCameraNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
