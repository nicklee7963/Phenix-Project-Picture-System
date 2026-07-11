import rclpy
from rclpy.node import Node
from std_srvs.srv import Trigger
import subprocess
import os
from datetime import datetime
import cv2  # 保留 OpenCV，為後續演算法做準備

class CameraServer(Node):
    def __init__(self):
        super().__init__('camera_server')
        self.srv = self.create_service(Trigger, 'capture_photo', self.capture_callback)
        self.get_logger().info('相機伺服器已啟動，等待拍照指令...')

    def capture_callback(self, request, response):
        self.get_logger().info('收到拍照指令，正在啟動相機...')
        
        # 使用當下時間作為檔名
        filename = datetime.now().strftime("%Y%m%d_%H%M%S") + '.jpg'
        filepath = os.path.join(os.getcwd(), filename)
        
        # 建立原生拍照指令：
        # -t 1000: 讓相機有 1 秒 (1000 毫秒) 的暖機時間來調整自動曝光與白平衡
        # --width / --height: 可以依照你的需求設定解析度
        cmd = ['libcamera-jpeg', '-o', filepath, '-t', '1000', '--width', '1920', '--height', '1080']
        
        try:
            # 執行系統指令
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and os.path.exists(filepath):
                response.success = True
                response.message = f'拍照成功！已儲存至: {filepath}'
                self.get_logger().info(response.message)
                
                # 測試將影像轉換為 NumPy Array
                # img_array = cv2.imread(filepath)
                # self.get_logger().info(f'影像已成功載入為 NumPy 陣列，形狀: {img_array.shape}')
            else:
                response.success = False
                response.message = f'拍照失敗，錯誤: {result.stderr}'
                self.get_logger().error(response.message)
                
        except Exception as e:
            response.success = False
            response.message = f'發生未預期例外: {str(e)}'
            self.get_logger().error(response.message)

        return response

def main(args=None):
    rclpy.init(args=args)
    node = CameraServer()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
