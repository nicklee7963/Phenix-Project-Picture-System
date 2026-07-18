import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

# 引入 Picamera2
from picamera2 import Picamera2

class PiCam2Publisher(Node):
    def __init__(self):
        super().__init__('picamera2_publisher')
        
        # 建立 Publisher，主題名稱為 'camera/image_raw'
        self.publisher_ = self.create_publisher(Image, 'camera/image_raw', 10)
        self.bridge = CvBridge()
        
        # 1. 實體化 Picamera2 物件
        self.picam2 = Picamera2()
        
        # 2. 設定相機組態
        # 我們直接要求輸出 RGB888 格式，解析度設為 640x480
        # 這種 numpy array 格式非常適合後續無縫接軌給 OpenCV 或神經網路處理
        config = self.picam2.create_video_configuration(main={"size": (640, 480), "format": "RGB888"})
        self.picam2.configure(config)
        
        # 3. 啟動相機硬體
        self.picam2.start()
        
        # 4. 設定計時器，控制發布頻率 (0.033 秒約等於 30 FPS)
        timer_period = 0.033  
        self.timer = self.create_timer(timer_period, self.timer_callback)
        
        self.get_logger().info('Picamera2 節點已啟動，開始發布影像！')

    def timer_callback(self):
        try:
            # 直接從相機記憶體中抓取最新的影像 (格式為 Numpy Array)
            frame = self.picam2.capture_array()
            
            # 將 RGB 的 Numpy Array 轉換為 ROS 能看懂的 Image 訊息
            msg = self.bridge.cv2_to_imgmsg(frame, encoding='rgb8')
            
            # 發布訊息
            self.publisher_.publish(msg)
            
        except Exception as e:
            self.get_logger().error(f'影像擷取失敗: {e}')

def main(args=None):
    rclpy.init(args=args)
    node = PiCam2Publisher()
    
    try:
        # 讓節點保持運行
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # 關閉程式時，確保安全釋放相機硬體
        node.picam2.stop()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
