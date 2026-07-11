import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
import cv2
import numpy as np

class SnapshotNode(Node):
    def __init__(self):
        super().__init__('snapshot_node')
        self.subscription = self.create_subscription(
            Image, '/camera/image_raw', self.callback, 10)
        self.saved = False

    def callback(self, msg):
        if not self.saved:
            # NV21 格式：高度為 H，寬度為 W，Y 平面大小為 H*W，UV 平面大小為 (H/2)*(W/2)*2
            # 總長度 = 1.5 * W * H
            width = msg.width
            height = msg.height
            
            # 將資料轉為 numpy 陣列
            data = np.frombuffer(msg.data, np.uint8)
            
            # 轉換 NV21 到 BGR
            yuv = data.reshape((height * 3 // 2, width))
            bgr_image = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR_NV21)
            
            cv2.imwrite('/ssl_ws/test_shot.jpg', bgr_image)
            self.get_logger().info(f'成功存檔！影像尺寸: {width}x{height}')
            self.saved = True
            rclpy.shutdown()

def main():
    rclpy.init()
    node = SnapshotNode()
    rclpy.spin(node)

if __name__ == '__main__':
    main()
