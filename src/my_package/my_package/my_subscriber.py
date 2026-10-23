import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class My_Subscriber(Node):
    def __init__(self):
        super().__init__('subscriber_node')
        self.sub = self.create_subscription(
            String, 
            'talking', 
            self.talking_callback ,
            10
            
        )

    def talking_callback(self, msg):
        self.get_logger().info(f'Received: "{msg.data}"')

def main(args=None):
    rclpy.init(args=args)
    node = My_Subscriber()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
