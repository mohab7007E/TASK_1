import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class My_Publisher(Node):
    def __init__(self):
        super().__init__('publisher_node')
        self.pub = self.create_publisher(
            String, 
            'talking', 
            10
        )
        self.timer = self.create_timer(
            1.0,
            self.publish_msg
        )

        self.counter=0

    def publish_msg(self):
        msg = String()
        msg.data = f'Hello from ros 2: {self.counter}'
        self.pub.publish(msg)
        self.get_logger().info(f'Published: "{msg.data}"')
        self.counter += 1

def main(args=None):
    rclpy.init(args=args)
    node = My_Publisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()