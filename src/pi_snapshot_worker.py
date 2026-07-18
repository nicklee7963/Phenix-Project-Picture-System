#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_srvs.srv import Trigger
from sensor_msgs.msg import Image, CompressedImage
from cv_bridge import CvBridge

# 引入感測器專用的 QoS 設定 (解決無法接收影像的關鍵)
from rclpy.qos import qos_profile_sensor_data

class PiSnapshotWorker(Node):
    def __init__(self):
        super().__init__('pi_snapshot_worker')
        
        self.bridge = CvBridge()
        self.latest_frame = None
        
        # 1. 訂閱 camera_ros 發布的原始影像
        # 將 Topic 改為 '/camera/image_raw' (若你的相機 topic 不同請更改)
        # 加上 qos_profile=qos_profile_sensor_data 確保能接收相機資料
        self.image_sub = self.create_subscription(
            Image, 
            '/camera/image_raw', 
            self.image_callback, 
            qos_profile=qos_profile_sensor_data)
            
        # 2. 準備發布壓縮影像給 PC
        self.snapshot_pub = self.create_publisher(
            CompressedImage, '/snapshot/compressed', 10)
            
        # 3. 提供 /take_snapshot 服務給 PC 呼叫
        self.srv = self.create_service(
            Trigger, '/take_snapshot', self.trigger_callback)
            
        self.get_logger().info('📸 Snapshot Worker 已啟動！等待 camera_ros 影像與 PC 指令...')

    def image_callback(self, msg):
        # 不斷更新記憶體中最熱騰騰的一幀畫面
        self.latest_frame = msg

    def trigger_callback(self, request, response):
        self.get_logger().info('收到 PC 拍照指令！')
        
        if self.latest_frame is None:
            response.success = False
            response.message = '尚未收到 camera_ros 的影像'
            self.get_logger().error('失敗：相機尚未發布影像，請確認 camera_node 有啟動。')
            return response

        try:
            # NV21 或是其他格式，cv_bridge 通常能自動處理轉換為 bgr8
            cv_image = self.bridge.imgmsg_to_cv2(self.latest_frame, desired_encoding='bgr8')
            
            compressed_msg = self.bridge.cv2_to_compressed_imgmsg(cv_image, dst_format='jpeg')
            self.snapshot_pub.publish(compressed_msg)
            
            response.success = True
            response.message = '影像壓縮並回傳成功'
            self.get_logger().info('✅ 影像已成功發送給 PC！')
            
        except Exception as e:
            response.success = False
            response.message = f'影像處理失敗: {str(e)}'
            self.get_logger().error(f'轉換失敗: {e}')
            
        return response

def main(args=None):
    rclpy.init(args=args)
    node = PiSnapshotWorker()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
