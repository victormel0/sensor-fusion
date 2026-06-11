import os

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    #region [Paths + env bridge]
    # Bake the venv_yolo bridge into the launch so the node imports ultralytics/torch/sklearn,
    # while rclpy + sensor_msgs_py still resolve from the ROS env.
    home = os.path.expanduser("~")
    repo = os.path.join(home, "Documents", "workspace", "sensor-fusion")
    venv_sp = os.path.join(repo, "venv_yolo", "lib", "python3.10", "site-packages")
    fusion_code = os.path.join(repo, "code", "fusion")
    # PREPEND venv + code/fusion to the INHERITED PYTHONPATH (set by sourcing the ROS env before
    # `ros2 launch`). A plain replace would drop the ROS python paths and break rclpy/sensor_msgs_py.
    inherited = os.environ.get("PYTHONPATH", "")
    pythonpath = os.pathsep.join([p for p in (venv_sp, fusion_code, inherited) if p])
    #endregion

    #region [Fusion node]
    fusion_node = Node(
        package="thesis_fusion",
        executable="fusion_node",
        name="fusion_node",
        output="screen",
        # `additional_env` MERGES with the inherited environment (overrides only PYTHONPATH),
        # so AMENT_PREFIX_PATH / LD_LIBRARY_PATH / ROS_DISTRO etc. are preserved.
        # to verify against current docs: the exact kwarg name on the launch_ros version on the box.
        additional_env={"PYTHONPATH": pythonpath},
        # arguments=["--profile", "--profile-window", "200"],  # optional: profiling under launch
    )
    #endregion

    return LaunchDescription([fusion_node])
