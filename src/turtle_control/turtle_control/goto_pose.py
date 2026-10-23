import math
import time
from std_srvs.srv import Empty
import rclpy
from rclpy.action import ActionServer
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from rclpy.parameter import Parameter
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from turtlesim.srv import SetPen, TeleportAbsolute


from my_interfaces.action import GoToPose 
from my_interfaces.srv import SetSpeeds   

class GoToPoseNode(Node):
    def __init__(self):
        super().__init__('goto_pose_node')
        self.callback_group = ReentrantCallbackGroup()

        
        self.declare_parameter('max_linear_speed', 2.0)
        self.declare_parameter('max_angular_speed', 1.0)

     #Action Server
        self._action_server = ActionServer(
            self,
            GoToPose,
            'go_to_pose',
            self.execute_callback,
            callback_group=self.callback_group
        )

        
        self.set_speeds_service = self.create_service(
            SetSpeeds,
            'set_speeds',
            self.set_speeds_callback,
            callback_group=self.callback_group
        )

        
        self.reset_service = self.create_service(
            Empty,
            'reset_turtle',
            self.reset_callback,
            callback_group=self.callback_group
        )

        
        self.clear_client = self.create_client(Empty, '/clear')
        self.teleport_client = self.create_client(TeleportAbsolute, '/turtle1/teleport_absolute')
        self.pen_client = self.create_client(SetPen, '/turtle1/set_pen')

        self.pose_sub = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_cb,
            10
        )

        self.cmd_pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.current_pose = None

        self.get_logger().info('Independent GoToPose Node Ready.')

    def pose_cb(self, msg):
        self.current_pose = msg

    def set_speeds_callback(self, request, response):
       
        if request.max_linear <= 0.0 or request.max_angular <= 0.0:
            self.get_logger().warn('Invalid speeds! Must be greater than 0.')
            response.success = False
            return response

        
        self.set_parameters([
            Parameter('max_linear_speed', Parameter.Type.DOUBLE, request.max_linear),
            Parameter('max_angular_speed', Parameter.Type.DOUBLE, request.max_angular),
        ])

        self.get_logger().info(
            f'Speeds updated -> Linear: {request.max_linear}, Angular: {request.max_angular}'
        )

        response.success = True
        return response

    
    async def reset_callback(self, request, response):
        self.get_logger().info('Resetting turtle...')
        
        
        pen_req = SetPen.Request()
        pen_req.off = 1
        await self.pen_client.call_async(pen_req)

        
        teleport_req = TeleportAbsolute.Request()
        teleport_req.x = 5.54
        teleport_req.y = 5.54
        teleport_req.theta = 0.0
        await self.teleport_client.call_async(teleport_req)

       
        await self.clear_client.call_async(Empty.Request())

        
        pen_req.off = 0
        await self.pen_client.call_async(pen_req)

        self.get_logger().info('Reset complete.')
        return response

    def execute_callback(self, goal_handle):
        target = goal_handle.request.goal_pose
        feedback = GoToPose.Feedback()
        result = GoToPose.Result()
        if not (0.0 <= target.x <= 11.0 and 0.0 <= target.y <= 11.0):
            self.get_logger().warn('Goal outside window (0-11), aborting.')
            goal_handle.abort()
            return resul

        self.get_logger().info(f'Received Goal: x={target.x}, y={target.y}, yaw={target.yaw}')

        
        while rclpy.ok():
            if self.current_pose is None:
                time.sleep(0.1)
                continue

           
            max_linear = self.get_parameter('max_linear_speed').value
            max_angular = self.get_parameter('max_angular_speed').value

            dx = target.x - self.current_pose.x
            dy = target.y - self.current_pose.y
            dist = math.hypot(dx, dy)

            feedback.distance_remaining = dist
            goal_handle.publish_feedback(feedback)

            if dist < 0.1:
                break

            target_angle = math.atan2(dy, dx)
            angle_err = target_angle - self.current_pose.theta
           
            angle_err = math.atan2(math.sin(angle_err), math.cos(angle_err))

            twist = Twist()
            if abs(angle_err) > 0.3:
                twist.linear.x = 0.0
            else:
                twist.linear.x = min(max_linear, max(0.2, 1.5 * dist))
            twist.angular.z = min(max_angular, max(-max_angular, 4.0 * angle_err))
            self.cmd_pub.publish(twist)
            time.sleep(0.1)

       
        self.cmd_pub.publish(Twist())
        time.sleep(0.1)

       
        while rclpy.ok():
            if self.current_pose is None:
                time.sleep(0.1)
                continue

            
            max_angular = self.get_parameter('max_angular_speed').value
            
            yaw_err = target.yaw - self.current_pose.theta
            yaw_err = math.atan2(math.sin(yaw_err), math.cos(yaw_err))

            if abs(yaw_err) < 0.05:
                break

            twist = Twist()
            twist.angular.z = min(max_angular, max(-max_angular, 4.0 * yaw_err))
            self.cmd_pub.publish(twist)
            time.sleep(0.1)

       
        self.cmd_pub.publish(Twist())
        
        goal_handle.succeed()
        result.success = True
        return result

def main(args=None):
    rclpy.init(args=args)
    node = GoToPoseNode()
    
    
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
