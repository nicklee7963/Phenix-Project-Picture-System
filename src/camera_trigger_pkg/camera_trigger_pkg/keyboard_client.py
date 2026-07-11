import rclpy
from rclpy.node import Node
from std_srvs.srv import Trigger
import sys

class KeyboardClient(Node):
    def __init__(self):
        super().__init__('keyboard_client')
        # 建立 Client，目標是名為 'capture_photo' 的 Service
        self.client = self.create_client(Trigger, 'capture_photo')
        
        # 檢查 Server 是否存在
        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('等待相機伺服器啟動中...')
            
        self.request = Trigger.Request()

    def send_request(self):
        # 非同步發送請求
        self.future = self.client.call_async(self.request)
        rclpy.spin_until_future_complete(self, self.future)
        return self.future.result()

def main(args=None):
    rclpy.init(args=args)
    node = KeyboardClient()

    try:
        while True:
            # 讀取終端機的鍵盤輸入
            user_input = input("按下 'Enter' 鍵拍攝照片 (輸入 'q' 退出): ")
            
            if user_input.lower() == 'q':
                break
                
            node.get_logger().info('正在發送拍照指令...')
            response = node.send_request()
            
            if response.success:
                node.get_logger().info(f'伺服器回傳: {response.message}')
            else:
                node.get_logger().warn(f'發生錯誤: {response.message}')
                
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
