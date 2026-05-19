import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, PointCloud2
from message_filters import ApproximateTimeSynchronizer, Subscriber

class SyncTest(Node):
    def __init__(self):
        super().__init__('sync_test')
        img_sub = Subscriber(self, Image, '/zed/zed_node/rgb/color/rect/image')
        pc_sub = Subscriber(self, PointCloud2, '/rslidar_points')
        self.sync = ApproximateTimeSynchronizer(
            [img_sub, pc_sub], queue_size=10, slop=0.1)
        self.sync.registerCallback(self.cb)
        self.count = 0

    def cb(self, img, pc):
        dt = abs((img.header.stamp.sec - pc.header.stamp.sec) * 1e9 +
                 (img.header.stamp.nanosec - pc.header.stamp.nanosec)) / 1e6
        self.count += 1
        self.get_logger().info(f'Pair {self.count}: dt = {dt:.1f} ms')

def main():
    rclpy.init()
    node = SyncTest()
    rclpy.spin(node)

if __name__ == '__main__':
    main()