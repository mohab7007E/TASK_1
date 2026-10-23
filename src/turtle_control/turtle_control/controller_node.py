import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from my_interfaces.srv import SetSpeeds

class ControllerNode(Node):
    def __init__(self):
        super().__init__('controller_node')
        
        
        self.declare_parameter('max_linear_speed', 2.0)
        self.declare_parameter('max_angular_speed', 1.0)
        
        
        self.srv = self.create_service(SetSpeeds, 'set_speeds', self.set_speeds_callback)
        self.get_logger().info('Controller Node started. Speed service is ready.')

    def set_speeds_callback(self, request, response):
        
        if request.max_linear <= 0.0 or request.max_angular <= 0.0:
            self.get_logger().warn('Invalid speeds! Speeds must be greater than 0.')
            response.success = False
            return response
        
         
        new_linear = Parameter('max_linear_speed', Parameter.Type.DOUBLE, request.max_linear)
        new_angular = Parameter('max_angular_speed', Parameter.Type.DOUBLE, request.max_angular)
        self.set_parameters([new_linear, new_angular])
        
        self.get_logger().info(f'Speeds updated -> Linear: {request.max_linear}, Angular: {request.max_angular}')
        response.success = True
        return response

def main(args=None):
    rclpy.init(args=args)
    node = ControllerNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()