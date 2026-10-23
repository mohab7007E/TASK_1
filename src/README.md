# Lab 1: ROS 2, Turtlesim, Actions & Services

**Course:** Design of Mechatronics Systems, Alexandria University, Faculty of Engineering
**ROS 2 version:** Jazzy (Ubuntu 24.04, Python 3.12)

## Team Members

| Name | ID |
|---|---|
| Ziad Ahmed Misbah | 9764 |
| Mohab Mohamed Abdelsatar | 9763 |
| Yassin Ossama Elsayed | 9581 |

---

## 1. What does this project do?

We control the **turtlesim** turtle with our own ROS 2 nodes. The system can:

1. Drive the turtle to any point `(x, y)` and turn it to a final angle `yaw` (**goToPose** action).
2. Clear the screen and put the turtle back at the start without drawing a line (**reset** service).
3. Change the max speeds while the system is running (**set_speeds** service and ROS parameters).
4. Draw a square by calling goToPose **4 times** (**draw_square** action).

Everything starts with **one launch file**.

---

## 2. Project structure

```
Lab1/
├── README.md
├── my_interfaces/          <- only message, action and service definitions
│   ├── msg/Target.msg
│   ├── action/GoToPose.action
│   ├── action/DrawSquare.action
│   ├── srv/SetSpeeds.srv
│   ├── CMakeLists.txt
│   └── package.xml
└── turtle_control/         <- the Python nodes, launch file and config
    ├── turtle_control/
    │   ├── goto_pose.py        (goToPose server + reset service + set_speeds service)
    │   └── square_movment.py   (square action server)
    ├── launch/system.launch.py
    ├── config/params.yaml
    ├── setup.py
    └── package.xml
```

> Note: the file is named `square_movment.py` (without the "e") on purpose. The name is used in `setup.py`.

---

## 3. The two packages

### `my_interfaces` (the "language" of our system)

| File | Type | Fields |
|---|---|---|
| `Target.msg` | message | `float64 x`, `float64 y`, `float64 yaw` |
| `GoToPose.action` | action | Goal: `Target goal_pose`, Result: `bool success`, Feedback: `float32 distance_remaining` |
| `DrawSquare.action` | action | Goal: `float32 side_length`, Result: `bool success`, Feedback: `int32 current_side` |
| `SetSpeeds.srv` | service | Request: `max_linear`, `max_angular`, Response: `bool success` |

### `turtle_control` (the nodes)

| Node | Executable | What it gives |
|---|---|---|
| `goto_pose_node` | `goto_pose_node` | action `/go_to_pose`, service `/reset_turtle`, service `/set_speeds`, parameters `max_linear_speed` and `max_angular_speed` |
| `square_movement_node` | `square_movement_node` | action `/draw_square` |
| `turtlesim` | started by the launch file | the simulator |

---

## 4. How it works (simple explanation)

### goToPose (`/go_to_pose`)
The server loops until the turtle arrives:

1. Read the turtle position from `/turtle1/pose`.
2. Compute the **distance** to the goal and the **angle error** (the angle error is wrapped between -pi and pi).
3. If the turtle is not facing the goal (error more than 0.3 rad), it **only turns**. Then it moves straight. This avoids drawing curves.
4. Publish speed commands to `/turtle1/cmd_vel`. The speed is limited by the two parameters.
5. Stop when the distance is less than `0.1`.
6. Rotate to the final `yaw` (stop when error is less than `0.05` rad).
7. Send **feedback** (`distance_remaining`) all the time and a **result** at the end.

The speed parameters are **read again in every loop**, so changing them takes effect immediately.

### Speed service (`/set_speeds`)
It checks the values. If any value is **zero or negative**, it refuses and returns `success: False`. Otherwise it updates the parameters of `goto_pose_node` and returns `success: True`.

### Square (`/draw_square`)
1. Check the side length. It must be more than 0 and less than about **5.46** so the square stays inside the window.
2. Call `/reset_turtle` and wait.
3. Send **4 goals** to `/go_to_pose`, one after the other. Wait for each one to finish before sending the next.
4. Send feedback `current_side` (1 to 4) and a result at the end.

The corners (side length = `s`, start = `(5.54, 5.54)`):

| Side | Goal x | Goal y | yaw |
|---|---|---|---|
| 1 | 5.54 + s | 5.54 | pi/2 |
| 2 | 5.54 + s | 5.54 + s | pi |
| 3 | 5.54 | 5.54 + s | -pi/2 |
| 4 | 5.54 | 5.54 | 0 |

---

## 5. Requirements checklist

| # | Requirement | Where |
|---|---|---|
| R1 | Run turtlesim | `system.launch.py` |
| R2 | Custom message (x, y, yaw) | `my_interfaces/msg/Target.msg` |
| R3 | goToPose action server | `goto_pose.py` |
| R4 | Reset service (uses turtlesim services) | `goto_pose.py` |
| R5 | Square action server (4 goToPose calls) | `square_movment.py` |
| R6 | Launch files | `launch/system.launch.py` |
| R7 | Speed parameters + service to change them | `goto_pose.py`, `config/params.yaml` |
| R8 | Organized packages | `my_interfaces`, `turtle_control` |

---

## 6. Build steps

### Requirements
- Ubuntu 24.04 with **ROS 2 Jazzy**
- Turtlesim: `sudo apt install ros-jazzy-turtlesim`

### Build (from a fresh workspace)

```bash
source /opt/ros/jazzy/setup.bash
mkdir -p ~/lab1_ws/src
cd ~/lab1_ws/src
git clone <YOUR_REPO_LINK> .
cd ~/lab1_ws
colcon build
source install/setup.bash
```

If you changed code, build again and source again:

```bash
cd ~/lab1_ws
colcon build --packages-select turtle_control
source install/setup.bash
```

> **Important:** every new terminal needs these two lines first:
> ```bash
> source /opt/ros/jazzy/setup.bash
> source ~/lab1_ws/install/setup.bash
> ```

---

## 7. How to run

### Run everything with one command

```bash
ros2 launch turtle_control system.launch.py
```

You should see:
- the turtlesim window,
- `Independent GoToPose Node Ready.`
- `Square action server ready.`

Open a **new terminal** (and source it) for the test commands below.

### Run by hand (optional, 3 terminals)

```bash
ros2 run turtlesim turtlesim_node
ros2 run turtle_control goto_pose_node
ros2 run turtle_control square_movement_node
```

---

## 8. Commands to test every requirement

### R1: turtlesim and nodes are running
```bash
ros2 node list
```
Expected: `/turtlesim`, `/goto_pose_node`, `/square_movement_node`.

### R2: custom interfaces exist
```bash
ros2 interface list | grep my_interfaces
ros2 interface show my_interfaces/msg/Target
ros2 interface show my_interfaces/action/GoToPose
ros2 interface show my_interfaces/action/DrawSquare
ros2 interface show my_interfaces/srv/SetSpeeds
```

### R3: goToPose action
```bash
ros2 action list
ros2 action send_goal /go_to_pose my_interfaces/action/GoToPose "{goal_pose: {x: 8.0, y: 8.0, yaw: 1.57}}" --feedback
```
Expected: the turtle goes to (8, 8), feedback shows `distance_remaining` going down, and the result is `success: true`.
Try other goals too (left, right, up, down, behind the turtle). Keep x and y between 0 and 11.

### R4: reset service
First move the turtle so it draws lines, then:
```bash
ros2 service call /reset_turtle std_srvs/srv/Empty
```
Expected: screen is clean and the turtle is back at the centre (about 5.54, 5.54) facing angle 0, with no line drawn while teleporting.
Check the pose:
```bash
ros2 topic echo /turtle1/pose --once
```

### R5: square action
```bash
ros2 action send_goal /draw_square my_interfaces/action/DrawSquare "{side_length: 3.0}" --feedback
```
Expected: the turtle goes back to the centre, draws a square, feedback shows `current_side` 1 to 4, and the result is `success: true`.
In the `goto_pose_node` terminal you will see `Received Goal` exactly **4 times**.
Run it twice in a row: the second run starts clean because of the reset.

A side that is too big is rejected:
```bash
ros2 action send_goal /draw_square my_interfaces/action/DrawSquare "{side_length: 6.0}"
```
Expected: `Goal was rejected`.

### R6: launch file
Close all terminals, open one new terminal, source the workspace and run only:
```bash
ros2 launch turtle_control system.launch.py
```

### R7: speed parameters and service
Read the parameters:
```bash
ros2 param list /goto_pose_node
ros2 param get /goto_pose_node max_linear_speed
ros2 param get /goto_pose_node max_angular_speed
```
Change them with the parameter tool:
```bash
ros2 param set /goto_pose_node max_linear_speed 0.5
```
Change both with our service:
```bash
ros2 service call /set_speeds my_interfaces/srv/SetSpeeds "{max_linear: 0.5, max_angular: 0.5}"
```
Expected: `success: True`. Send a goal again and the turtle moves **slower**.

Invalid value (must be refused):
```bash
ros2 service call /set_speeds my_interfaces/srv/SetSpeeds "{max_linear: 0.0, max_angular: 0.5}"
```
Expected: `success: False`.

You can also change the speed **while the turtle is moving**, because the parameters are read in every loop.

---

## 9. Parameters (config file)

`turtle_control/config/params.yaml`:

```yaml
goto_pose_node:
  ros__parameters:
    max_linear_speed: 2.0
    max_angular_speed: 1.0
```

The launch file loads this file. To change the default speeds, edit the numbers, then rebuild and launch again:

```bash
cd ~/lab1_ws
colcon build --packages-select turtle_control
source install/setup.bash
ros2 launch turtle_control system.launch.py
```

---

## 10. Common problems and fixes

| Problem | Fix |
|---|---|
| `Package not found` or `launch file not found` | You forgot `source ~/lab1_ws/install/setup.bash` in this terminal, or you did not rebuild. |
| `No executable found` | Rebuild: `colcon build --packages-select turtle_control`, then source again. |
| Goal is rejected or nothing happens | The server is not running. Check `ros2 action list`. |
| Turtle never arrives | The goal is outside the window. Use x and y between 0 and 11. |
| Speed change has no effect | Make sure you call `/set_speeds` on the running system, then send a new goal. |
| Python `NameError` about `_name_` or `_init_` | A double underscore was lost when copying code. It must be `__name__`, `__init__`, `__main__`. |

---

## 11. Quick study notes

- **Message**: data that is sent on a topic (our `Target` has x, y, yaw).
- **Service**: one request, one answer, fast (reset, set_speeds).
- **Action**: a long task with feedback and a result (goToPose, draw_square).
- **Parameter**: a setting inside a node that can be changed while it runs (max speeds).
- **Launch file**: starts many nodes and loads parameters with one command.
- **Callback group (Reentrant) + MultiThreadedExecutor**: lets the node answer services and pose messages while an action is still running.

## Bonus (Rosbag Recording & Playback)
To record and play back the turtle's square movement:
- To play the recorded bag:
  ```bash
  ros2 bag play final_bonus_bag


## steps to run the whole task with the bonus

## open terminal 1
cd ~/TASK
source install/setup.bash
ros2 launch turtle_control system.launch.py
## then open terminal 2
cd ~/TASK
source install/setup.bash
ros2 bag record -o final_bonus_bag_3 /turtle1/cmd_vel /turtle1/pose  ## to record the move for the bonus part  ## (final_bonus_bag_3 ) is the name of the file recorde (change it freely)
## then open terminal 3
cd ~/TASK
source install/setup.bash
ros2 action send_goal /draw_square my_interfaces/action/DrawSquare "{side_length: 3.0}"  ## the movement function
 

 ## then wait to complete the square.
 ## then go to terminal 2 and press (Ctrl + C) to stop recording and save it. 

 ## back to terminal 3
 ros2 service call /reset_turtle std_srvs/srv/Empty  ## reset and back the turtle to the middle
 ros2 bag play final_bonus_bag  ## to play the recorded 


