import math

import rclpy
from rclpy.action import ActionClient, ActionServer, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from std_srvs.srv import Empty

from my_interfaces.action import DrawSquare, GoToPose


START_X = 5.54
START_Y = 5.54
MAX_COORD = 11.0


class SquareMovementNode(Node):
    def __init__(self):
        super().__init__('square_movement_node')
        self.cb_group = ReentrantCallbackGroup()

        self._action_server = ActionServer(
            self,
            DrawSquare,
            'draw_square',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            callback_group=self.cb_group,
        )

        self.goto_client = ActionClient(
            self, GoToPose, 'go_to_pose', callback_group=self.cb_group
        )
        self.reset_client = self.create_client(
            Empty, 'reset_turtle', callback_group=self.cb_group
        )

        self.get_logger().info('Square action server ready.')

    def goal_callback(self, goal_request):
        side = goal_request.side_length
        if side <= 0.0 or START_X + side >= MAX_COORD or START_Y + side >= MAX_COORD:
            self.get_logger().warn(
                f'Rejected side_length={side}. Must be > 0 and < {MAX_COORD - START_X:.2f}'
            )
            return GoalResponse.REJECT
        return GoalResponse.ACCEPT

    async def execute_callback(self, goal_handle):
        side = goal_handle.request.side_length
        result = DrawSquare.Result()
        feedback = DrawSquare.Feedback()

        # 1) Reset first
        self.get_logger().info('Resetting turtle...')
        await self.reset_client.call_async(Empty.Request())

        # 2) The four corners (yaw = direction of the NEXT side)
        corners = [
            (START_X + side, START_Y, math.pi / 2),
            (START_X + side, START_Y + side, math.pi),
            (START_X, START_Y + side, -math.pi / 2),
            (START_X, START_Y, 0.0),
        ]

        # 3) Four goals, one after the other
        for i, (x, y, yaw) in enumerate(corners, start=1):
            feedback.current_side = i
            goal_handle.publish_feedback(feedback)
            self.get_logger().info(f'Side {i}: going to ({x:.2f}, {y:.2f})')

            goal_msg = GoToPose.Goal()
            goal_msg.goal_pose.x = x
            goal_msg.goal_pose.y = y
            goal_msg.goal_pose.yaw = yaw

            send_future = self.goto_client.send_goal_async(goal_msg)
            gh = await send_future
            if not gh.accepted:
                self.get_logger().error(f'Side {i} rejected by go_to_pose')
                goal_handle.abort()
                result.success = False
                return result

            res = await gh.get_result_async()
            if not res.result.success:
                self.get_logger().error(f'Side {i} failed')
                goal_handle.abort()
                result.success = False
                return result

        goal_handle.succeed()
        result.success = True
        self.get_logger().info('Square complete.')
        return result


def main(args=None):
    rclpy.init(args=args)
    node = SquareMovementNode()
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
