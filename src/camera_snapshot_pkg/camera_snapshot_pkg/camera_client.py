import rclpy
from rclpy.node import Node
from snapshot_interfaces.srv import TakePhoto # 匯入自定義的 Service

class CameraClient(Node):
    def __init__(self):
        super().__init__('camera_client')
        self.cli = self.create_client(TakePhoto, 'take_snapshot')
        
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('等待相機 Server 上線中...')
            
        self.req = TakePhoto.Request()

    def send_request(self, label_name):
        self.req.label = label_name
        self.future = self.cli.call_async(self.req)
        rclpy.spin_until_future_complete(self, self.future)
        return self.future.result()

def main():
    rclpy.init()
    node = CameraClient()

    try:
        while rclpy.ok():
            # 讓使用者自訂照片前綴標籤
            label_input = input("\n👉 請輸入照片標籤 (直接按 Enter 預設為 'test'，輸入 'q' 離開): ")
            
            if label_input.lower() == 'q':
                break
                
            if label_input.strip() == '':
                label_input = 'test'
            
            node.get_logger().info('發送拍照請求...')
            response = node.send_request(label_input)
            
            # 讀取自訂的 Response
            if response.success:
                node.get_logger().info(f'✅ 存檔成功！解析度: {response.width}x{response.height}')
                node.get_logger().info(f'✅ 檔案位置: {response.filepath}')
            else:
                node.get_logger().error('❌ 存檔失敗')
                
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
