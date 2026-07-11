import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from snapshot_interfaces.srv import TakePhoto  # 匯入自定義的 Service
import cv2
import numpy as np
import time

class CameraServer(Node):
    def __init__(self):
        super().__init__('camera_server')
        self.latest_msg = None
        self.subscription = self.create_subscription(
            Image, '/camera/image_raw', self.image_callback, 10)
        
        # 建立自定義的 Service Server
        self.srv = self.create_service(TakePhoto, 'take_snapshot', self.snapshot_callback)
        self.get_logger().info('📸 相機 Server 已啟動，等待 Client 發送標籤指令...')

    def image_callback(self, msg):
        self.latest_msg = msg

    def snapshot_callback(self, request, response):
        self.get_logger().info(f'收到拍照請求！標籤名稱: {request.label}')
        
        if self.latest_msg is None:
            response.success = False
            response.filepath = ''
            return response

        try:
            msg = self.latest_msg
            width = msg.width
            height = msg.height

            data = np.frombuffer(msg.data, np.uint8)
            yuv = data.reshape((height * 3 // 2, width))
            bgr_image = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR_NV21)

            # 使用 Client 傳來的 label 作為檔名的一部分
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            save_path = f'/ssl_ws/{request.label}_{timestamp}.jpg'
            
            cv2.imwrite(save_path, bgr_image)
            
            # 填寫自定義的 Response 資料
            response.success = True
            response.filepath = save_path
            response.width = width
            response.height = height
            
            self.get_logger().info(f'成功存檔！路徑: {save_path}')

        except Exception as e:
            response.success = False
            response.filepath = f'錯誤: {str(e)}'
            
        return response

def main():
    rclpy.init()
    node = CameraServer()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
