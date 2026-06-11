# Day 1 (d19) live-node skeleton manifest -- 2026-06-08

**Goal:** thesis_fusion package + synced subscribers + model-load-once + stub publisher on bag playback.

**Initial free disk on $HOME:** 148G

## P0 interface probes (run-first)
user@GTW-ONX1-C1FDGRMU:~/Documents/workspace/sensor-fusion$ ros2 topic info -v /zed/zed_node/rgb/color/rect/image
Type: sensor_msgs/msg/Image

Publisher count: 1

Node name: zed_node
Node namespace: /zed
Topic type: sensor_msgs/msg/Image
Endpoint type: PUBLISHER
GID: 01.0f.e7.df.96.6b.d4.86.00.00.00.00.00.00.26.03.00.00.00.00.00.00.00.00
QoS profile:
  Reliability: RELIABLE
  History (Depth): UNKNOWN
  Durability: VOLATILE
  Lifespan: Infinite
  Deadline: Infinite
  Liveliness: AUTOMATIC
  Liveliness lease duration: Infinite

Subscription count: 0

user@GTW-ONX1-C1FDGRMU:~/Documents/workspace/sensor-fusion$ ros2 topic info -v /rslidar_points
Type: sensor_msgs/msg/PointCloud2

Publisher count: 1

Node name: rslidar_points_destination_0
Node namespace: /rslidar_sdk
Topic type: sensor_msgs/msg/PointCloud2
Endpoint type: PUBLISHER
GID: 01.0f.e7.df.98.6b.b0.6f.00.00.00.00.00.00.21.03.00.00.00.00.00.00.00.00
QoS profile:
  Reliability: RELIABLE
  History (Depth): UNKNOWN
  Durability: VOLATILE
  Lifespan: Infinite
  Deadline: Infinite
  Liveliness: AUTOMATIC
  Liveliness lease duration: Infinite

Subscription count: 1

Node name: rviz
Node namespace: /rviz2
Topic type: sensor_msgs/msg/PointCloud2
Endpoint type: SUBSCRIPTION
GID: 01.0f.e7.df.9a.6b.40.01.00.00.00.00.00.00.20.04.00.00.00.00.00.00.00.00
QoS profile:
  Reliability: RELIABLE
  History (Depth): UNKNOWN
  Durability: VOLATILE
  Lifespan: Infinite
  Deadline: Infinite
  Liveliness: AUTOMATIC
  Liveliness lease duration: Infinite

user@GTW-ONX1-C1FDGRMU:~/Documents/workspace/sensor-fusion$ ros2 interface list | grep -iE 'detection|marker'
    visualization_msgs/msg/ImageMarker
    visualization_msgs/msg/InteractiveMarker
    visualization_msgs/msg/InteractiveMarkerControl
    visualization_msgs/msg/InteractiveMarkerFeedback
    visualization_msgs/msg/InteractiveMarkerInit
    visualization_msgs/msg/InteractiveMarkerPose
    visualization_msgs/msg/InteractiveMarkerUpdate
    visualization_msgs/msg/Marker
    visualization_msgs/msg/MarkerArray
    visualization_msgs/srv/GetInteractiveMarkers
user@GTW-ONX1-C1FDGRMU:~/Documents/workspace/sensor-fusion$ ros2 topic echo --once /rslidar_points --field fields
[sensor_msgs.msg.PointField(name='x', offset=0, datatype=7, count=1), sensor_msgs.msg.PointField(name='y', offset=4, datatype=7, count=1), sensor_msgs.msg.PointField(name='z', offset=8, datatype=7, count=1), sensor_msgs.msg.PointField(name='intensity', offset=12, datatype=7, count=1)]
---
user@GTW-ONX1-C1FDGRMU:~/Documents/workspace/sensor-fusion$ source venv_yolo/bin/activate && python -c "import ultralytics, torch; print('ultralytics', ultralytics.__version__, 'torch', torch.__version__)"
ultralytics 8.4.60 torch 2.8.0
(venv_yolo) user@GTW-ONX1-C1FDGRMU:~/Documents/workspace/sensor-fusion$ printenv ROS_DISTRO
humble


- RGB topic resolved type / QoS: sensor_msgs/msg/Image; RELIABLE, VOLATILE (live zed_node). History depth reported UNKNOWN by `topic info -v` (rmw quirk, not a problem; Reliability+Durability are the axes that matter for matching).
- LiDAR topic resolved type / QoS: sensor_msgs/msg/PointCloud2; RELIABLE, VOLATILE (live rslidar_sdk). best_effort? NO -> a default (RELIABLE/VOLATILE, depth 10) subscriber is compatible; no special QoS needed.
- Detection msg chosen: vision_msgs/msg/Detection3DArray -- BUT vision_msgs is NOT installed (P0.3 returned only visualization_msgs). Installed after with `sudo apt install ros-humble-vision-msgs`.
- Marker msg chosen: visualization_msgs/msg/MarkerArray (installed, confirmed in P0.3).
- PointCloud2 fields (name@offset:datatype): x@0:float32, y@4:float32, z@8:float32, intensity@12:float32. FOUR fields (16-byte point), NOT the offline .bin's 5 channels -> the live node reads xyz BY FIELD NAME, it must not reuse the offline reshape(-1,5).

## Ros2 PKG Create

user@GTW-ONX1-C1FDGRMU:~/Documents/workspace/sensor-fusion$ ros2 pkg create --build-type ament_python thesis_fusion     --dependencies rclpy sensor_msgs geometry_msgs std_msgs message_filters visualization_msgs vision_msgs
going to create a new package
package name: thesis_fusion
destination directory: /home/user/Documents/workspace/sensor-fusion
package format: 3
version: 0.0.0
description: TODO: Package description
maintainer: ['user <victor.bezerramelo@deepware.it>']
licenses: ['TODO: License declaration']
build type: ament_python
dependencies: ['rclpy', 'sensor_msgs', 'geometry_msgs', 'std_msgs', 'message_filters', 'visualization_msgs', 'vision_msgs']
creating folder ./thesis_fusion
creating ./thesis_fusion/package.xml
creating source folder
creating folder ./thesis_fusion/thesis_fusion
creating ./thesis_fusion/setup.py
creating ./thesis_fusion/setup.cfg
creating folder ./thesis_fusion/resource
creating ./thesis_fusion/resource/thesis_fusion
creating ./thesis_fusion/thesis_fusion/__init__.py
creating folder ./thesis_fusion/test
creating ./thesis_fusion/test/test_copyright.py
creating ./thesis_fusion/test/test_flake8.py
creating ./thesis_fusion/test/test_pep257.py

[WARNING]: Unknown license 'TODO: License declaration'.  This has been set in the package.xml, but no LICENSE file has been created.
It is recommended to use one of the ament license identitifers:
Apache-2.0
BSL-1.0
BSD-2.0
BSD-2-Clause
BSD-3-Clause
GPL-3.0-only
LGPL-3.0-only
MIT
MIT-0
user@GTW-ONX1-C1FDGRMU:~/Documents/workspace/sensor-fusion$ 

## Problems found in: colcon build --packages-select thesis_fusion --symlink-install

### First attempt: 

user@GTW-ONX1-C1FDGRMU:~/Documents/workspace/sensor-fusion$ colcon build --packages-select thesis_fusion --symlink-install
/home/user/.local/lib/python3.10/site-packages/torch/cuda/__init__.py:187: UserWarning: CUDA initialization: The NVIDIA driver on your system is too old (found version 12060). Please update your GPU driver by downloading and installing a new version from the URL: http://www.nvidia.com/Download/index.aspx Alternatively, go to: https://pytorch.org to install a PyTorch version that has been compiled with your version of the CUDA driver. (Triggered internally at /pytorch/c10/cuda/CUDAFunctions.cpp:119.)
  return torch._C._cuda_getDeviceCount() > 0
W0608 13:26:09.052000 30812 torch/utils/cpp_extension.py:140] No CUDA runtime is found, using CUDA_HOME='/usr/local/cuda'
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "/usr/lib/python3.10/distutils/core.py", line 225, in run_setup
    raise RuntimeError(("'distutils.core.setup()' was never called -- "
RuntimeError: 'distutils.core.setup()' was never called -- perhaps 'setup.py' is not a Distutils setup script?
[4.289s] ERROR:colcon.colcon_core.package_identification:Exception in package identification extension 'python_setup_py' in 'third_party/OpenPCDet': Command '['/usr/bin/python3', '-c', 'import sys;from contextlib import suppress;exec("with suppress(ImportError):    from setuptools.extern.packaging.specifiers    import SpecifierSet");exec("with suppress(ImportError):    from packaging.specifiers import SpecifierSet");from distutils.core import run_setup;dist = run_setup(    \'setup.py\', script_args=(\'--dry-run\',), stop_after=\'config\');skip_keys = (\'cmdclass\', \'distclass\', \'ext_modules\', \'metadata\');data = {    key: value for key, value in dist.__dict__.items()     if (        not key.startswith(\'_\') and         not callable(value) and         key not in skip_keys and         key not in dist.display_option_names    )};data[\'metadata\'] = {    k: v for k, v in dist.metadata.__dict__.items()     if k not in (\'license_files\', \'provides_extras\')};sys.stdout.buffer.write(repr(data).encode(\'utf-8\'))']' returned non-zero exit status 1.
Traceback (most recent call last):
  File "/usr/lib/python3/dist-packages/colcon_core/package_identification/__init__.py", line 144, in _identify
    retval = extension.identify(_reused_descriptor_instance)
  File "/usr/lib/python3/dist-packages/colcon_python_setup_py/package_identification/python_setup_py.py", line 48, in identify
    config = get_setup_information(setup_py)
  File "/usr/lib/python3/dist-packages/colcon_python_setup_py/package_identification/python_setup_py.py", line 249, in get_setup_information
    _setup_information_cache[hashable_env] = _get_setup_information(
  File "/usr/lib/python3/dist-packages/colcon_python_setup_py/package_identification/python_setup_py.py", line 296, in _get_setup_information
    result = subprocess.run(
  File "/usr/lib/python3.10/subprocess.py", line 526, in run
    raise CalledProcessError(retcode, process.args,
subprocess.CalledProcessError: Command '['/usr/bin/python3', '-c', 'import sys;from contextlib import suppress;exec("with suppress(ImportError):    from setuptools.extern.packaging.specifiers    import SpecifierSet");exec("with suppress(ImportError):    from packaging.specifiers import SpecifierSet");from distutils.core import run_setup;dist = run_setup(    \'setup.py\', script_args=(\'--dry-run\',), stop_after=\'config\');skip_keys = (\'cmdclass\', \'distclass\', \'ext_modules\', \'metadata\');data = {    key: value for key, value in dist.__dict__.items()     if (        not key.startswith(\'_\') and         not callable(value) and         key not in skip_keys and         key not in dist.display_option_names    )};data[\'metadata\'] = {    k: v for k, v in dist.metadata.__dict__.items()     if k not in (\'license_files\', \'provides_extras\')};sys.stdout.buffer.write(repr(data).encode(\'utf-8\'))']' returned non-zero exit status 1.

^CTraceback (most recent call last):
  File "<string>", line 1, in <module>

### Second attempt: after creating third_party/OpenPCDet/COLCON_IGNORE
user@GTW-ONX1-C1FDGRMU:~/Documents/workspace/sensor-fusion$ colcon build --packages-select thesis_fusion --symlink-install
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "/usr/lib/python3.10/distutils/core.py", line 215, in run_setup
    exec(f.read(), g)
  File "<string>", line 15, in <module>
ModuleNotFoundError: No module named 'pccm'
[1.138s] ERROR:colcon.colcon_core.package_identification:Exception in package identification extension 'python_setup_py' in 'third_party/spconv': Command '['/usr/bin/python3', '-c', 'import sys;from contextlib import suppress;exec("with suppress(ImportError):    from setuptools.extern.packaging.specifiers    import SpecifierSet");exec("with suppress(ImportError):    from packaging.specifiers import SpecifierSet");from distutils.core import run_setup;dist = run_setup(    \'setup.py\', script_args=(\'--dry-run\',), stop_after=\'config\');skip_keys = (\'cmdclass\', \'distclass\', \'ext_modules\', \'metadata\');data = {    key: value for key, value in dist.__dict__.items()     if (        not key.startswith(\'_\') and         not callable(value) and         key not in skip_keys and         key not in dist.display_option_names    )};data[\'metadata\'] = {    k: v for k, v in dist.metadata.__dict__.items()     if k not in (\'license_files\', \'provides_extras\')};sys.stdout.buffer.write(repr(data).encode(\'utf-8\'))']' returned non-zero exit status 1.
Traceback (most recent call last):
  File "/usr/lib/python3/dist-packages/colcon_core/package_identification/__init__.py", line 144, in _identify
    retval = extension.identify(_reused_descriptor_instance)
  File "/usr/lib/python3/dist-packages/colcon_python_setup_py/package_identification/python_setup_py.py", line 48, in identify
    config = get_setup_information(setup_py)
  File "/usr/lib/python3/dist-packages/colcon_python_setup_py/package_identification/python_setup_py.py", line 249, in get_setup_information
    _setup_information_cache[hashable_env] = _get_setup_information(
  File "/usr/lib/python3/dist-packages/colcon_python_setup_py/package_identification/python_setup_py.py", line 296, in _get_setup_information
    result = subprocess.run(
  File "/usr/lib/python3.10/subprocess.py", line 526, in run
    raise CalledProcessError(retcode, process.args,
subprocess.CalledProcessError: Command '['/usr/bin/python3', '-c', 'import sys;from contextlib import suppress;exec("with suppress(ImportError):    from setuptools.extern.packaging.specifiers    import SpecifierSet");exec("with suppress(ImportError):    from packaging.specifiers import SpecifierSet");from distutils.core import run_setup;dist = run_setup(    \'setup.py\', script_args=(\'--dry-run\',), stop_after=\'config\');skip_keys = (\'cmdclass\', \'distclass\', \'ext_modules\', \'metadata\');data = {    key: value for key, value in dist.__dict__.items()     if (        not key.startswith(\'_\') and         not callable(value) and         key not in skip_keys and         key not in dist.display_option_names    )};data[\'metadata\'] = {    k: v for k, v in dist.metadata.__dict__.items()     if k not in (\'license_files\', \'provides_extras\')};sys.stdout.buffer.write(repr(data).encode(\'utf-8\'))']' returned non-zero exit status 1.

Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "/usr/lib/python3.10/distutils/core.py", line 225, in run_setup
    raise RuntimeError(("'distutils.core.setup()' was never called -- "
RuntimeError: 'distutils.core.setup()' was never called -- perhaps 'setup.py' is not a Distutils setup script?
[2.908s] ERROR:colcon.colcon_core.package_identification:Exception in package identification extension 'python_setup_py' in 'venv_openpcdet/lib/python3.10/site-packages/numpy/_typing': Command '['/usr/bin/python3', '-c', 'import sys;from contextlib import suppress;exec("with suppress(ImportError):    from setuptools.extern.packaging.specifiers    import SpecifierSet");exec("with suppress(ImportError):    from packaging.specifiers import SpecifierSet");from distutils.core import run_setup;dist = run_setup(    \'setup.py\', script_args=(\'--dry-run\',), stop_after=\'config\');skip_keys = (\'cmdclass\', \'distclass\', \'ext_modules\', \'metadata\');data = {    key: value for key, value in dist.__dict__.items()     if (        not key.startswith(\'_\') and         not callable(value) and         key not in skip_keys and         key not in dist.display_option_names    )};data[\'metadata\'] = {    k: v for k, v in dist.metadata.__dict__.items()     if k not in (\'license_files\', \'provides_extras\')};sys.stdout.buffer.write(repr(data).encode(\'utf-8\'))']' returned non-zero exit status 1.
Traceback (most recent call last):
  File "/usr/lib/python3/dist-packages/colcon_core/package_identification/__init__.py", line 144, in _identify
    retval = extension.identify(_reused_descriptor_instance)
  File "/usr/lib/python3/dist-packages/colcon_python_setup_py/package_identification/python_setup_py.py", line 48, in identify
    config = get_setup_information(setup_py)
  File "/usr/lib/python3/dist-packages/colcon_python_setup_py/package_identification/python_setup_py.py", line 249, in get_setup_information
    _setup_information_cache[hashable_env] = _get_setup_information(
  File "/usr/lib/python3/dist-packages/colcon_python_setup_py/package_identification/python_setup_py.py", line 296, in _get_setup_information
    result = subprocess.run(
  File "/usr/lib/python3.10/subprocess.py", line 526, in run
    raise CalledProcessError(retcode, process.args,
subprocess.CalledProcessError: Command '['/usr/bin/python3', '-c', 'import sys;from contextlib import suppress;exec("with suppress(ImportError):    from setuptools.extern.packaging.specifiers    import SpecifierSet");exec("with suppress(ImportError):    from packaging.specifiers import SpecifierSet");from distutils.core import run_setup;dist = run_setup(    \'setup.py\', script_args=(\'--dry-run\',), stop_after=\'config\');skip_keys = (\'cmdclass\', \'distclass\', \'ext_modules\', \'metadata\');data = {    key: value for key, value in dist.__dict__.items()     if (        not key.startswith(\'_\') and         not callable(value) and         key not in skip_keys and         key not in dist.display_option_names    )};data[\'metadata\'] = {    k: v for k, v in dist.metadata.__dict__.items()     if k not in (\'license_files\', \'provides_extras\')};sys.stdout.buffer.write(repr(data).encode(\'utf-8\'))']' returned non-zero exit status 1.

Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "/usr/lib/python3.10/distutils/core.py", line 225, in run_setup
    raise RuntimeError(("'distutils.core.setup()' was never called -- "
RuntimeError: 'distutils.core.setup()' was never called -- perhaps 'setup.py' is not a Distutils setup script?
[3.422s] ERROR:colcon.colcon_core.package_identification:Exception in package identification extension 'python_setup_py' in 'venv_openpcdet/lib/python3.10/site-packages/numpy/array_api': Command '['/usr/bin/python3', '-c', 'import sys;from contextlib import suppress;exec("with suppress(ImportError):    from setuptools.extern.packaging.specifiers    import SpecifierSet");exec("with suppress(ImportError):    from packaging.specifiers import SpecifierSet");from distutils.core import run_setup;dist = run_setup(    \'setup.py\', script_args=(\'--dry-run\',), stop_after=\'config\');skip_keys = (\'cmdclass\', \'distclass\', \'ext_modules\', \'metadata\');data = {    key: value for key, value in dist.__dict__.items()     if (        not key.startswith(\'_\') and         not callable(value) and         key not in skip_keys and         key not in dist.display_option_names    )};data[\'metadata\'] = {    k: v for k, v in dist.metadata.__dict__.items()     if k not in (\'license_files\', \'provides_extras\')};sys.stdout.buffer.write(repr(data).encode(\'utf-8\'))']' returned non-zero exit status 1.
Traceback (most recent call last):
  File "/usr/lib/python3/dist-packages/colcon_core/package_identification/__init__.py", line 144, in _identify
    retval = extension.identify(_reused_descriptor_instance)
  File "/usr/lib/python3/dist-packages/colcon_python_setup_py/package_identification/python_setup_py.py", line 48, in identify
    config = get_setup_information(setup_py)
  File "/usr/lib/python3/dist-packages/colcon_python_setup_py/package_identification/python_setup_py.py", line 249, in get_setup_information
    _setup_information_cache[hashable_env] = _get_setup_information(
  File "/usr/lib/python3/dist-packages/colcon_python_setup_py/package_identification/python_setup_py.py", line 296, in _get_setup_information
    result = subprocess.run(
  File "/usr/lib/python3.10/subprocess.py", line 526, in run
    raise CalledProcessError(retcode, process.args,
subprocess.CalledProcessError: Command '['/usr/bin/python3', '-c', 'import sys;from contextlib import suppress;exec("with suppress(ImportError):    from setuptools.extern.packaging.specifiers    import SpecifierSet");exec("with suppress(ImportError):    from packaging.specifiers import SpecifierSet");from distutils.core import run_setup;dist = run_setup(    \'setup.py\', script_args=(\'--dry-run\',), stop_after=\'config\');skip_keys = (\'cmdclass\', \'distclass\', \'ext_modules\', \'metadata\');data = {    key: value for key, value in dist.__dict__.items()     if (        not key.startswith(\'_\') and         not callable(value) and         key not in skip_keys and         key not in dist.display_option_names    )};data[\'metadata\'] = {    k: v for k, v in dist.metadata.__dict__.items()     if k not in (\'license_files\', \'provides_extras\')};sys.stdout.buffer.write(repr(data).encode(\'utf-8\'))']' returned non-zero exit status 1.

Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "/usr/lib/python3.10/distutils/core.py", line 225, in run_setup
    raise RuntimeError(("'distutils.core.setup()' was never called -- "
RuntimeError: 'distutils.core.setup()' was never called -- perhaps 'setup.py' is not a Distutils setup script?
[3.920s] ERROR:colcon.colcon_core.package_identification:Exception in package identification extension 'python_setup_py' in 'venv_openpcdet/lib/python3.10/site-packages/numpy/compat': Command '['/usr/bin/python3', '-c', 'import sys;from contextlib import suppress;exec("with suppress(ImportError):    from setuptools.extern.packaging.specifiers    import SpecifierSet");exec("with suppress(ImportError):    from packaging.specifiers import SpecifierSet");from distutils.core import run_setup;dist = run_setup(    \'setup.py\', script_args=(\'--dry-run\',), stop_after=\'config\');skip_keys = (\'cmdclass\', \'distclass\', \'ext_modules\', \'metadata\');data = {    key: value for key, value in dist.__dict__.items()     if (        not key.startswith(\'_\') and         not callable(value) and         key not in skip_keys and         key not in dist.display_option_names    )};data[\'metadata\'] = {    k: v for k, v in dist.metadata.__dict__.items()     if k not in (\'license_files\', \'provides_extras\')};sys.stdout.buffer.write(repr(data).encode(\'utf-8\'))']' returned non-zero exit status 1.
Traceback (most recent call last):
  File "/usr/lib/python3/dist-packages/colcon_core/package_identification/__init__.py", line 144, in _identify
    retval = extension.identify(_reused_descriptor_instance)
  File "/usr/lib/python3/dist-packages/colcon_python_setup_py/package_identification/python_setup_py.py", line 48, in identify
    config = get_setup_information(setup_py)
  File "/usr/lib/python3/dist-packages/colcon_python_setup_py/package_identification/python_setup_py.py", line 249, in get_setup_information
    _setup_information_cache[hashable_env] = _get_setup_information(
  File "/usr/lib/python3/dist-packages/colcon_python_setup_py/package_identification/python_setup_py.py", line 296, in _get_setup_information
    result = subprocess.run(
  File "/usr/lib/python3.10/subprocess.py", line 526, in run
    raise CalledProcessError(retcode, process.args,
subprocess.CalledProcessError: Command '['/usr/bin/python3', '-c', 'import sys;from contextlib import suppress;exec("with suppress(ImportError):    from setuptools.extern.packaging.specifiers    import SpecifierSet");exec("with suppress(ImportError):    from packaging.specifiers import SpecifierSet");from distutils.core import run_setup;dist = run_setup(    \'setup.py\', script_args=(\'--dry-run\',), stop_after=\'config\');skip_keys = (\'cmdclass\', \'distclass\', \'ext_modules\', \'metadata\');data = {    key: value for key, value in dist.__dict__.items()     if (        not key.startswith(\'_\') and         not callable(value) and         key not in skip_keys and         key not in dist.display_option_names    )};data[\'metadata\'] = {    k: v for k, v in dist.metadata.__dict__.items()     if k not in (\'license_files\', \'provides_extras\')};sys.stdout.buffer.write(repr(data).encode(\'utf-8\'))']' returned non-zero exit status 1.

^Cuser@GTW-ONX1-C1FDGRMU:~/Documents/workspace/sensor-fusion$ 

### Third attempt: cd ~/Documents/workspace/sensor-fusion/ros2_ws/src

user@GTW-ONX1-C1FDGRMU:~/Documents/workspace/sensor-fusion/ros2_ws/src$ colcon build --packages-select thesis_fusion --symlink-install
Starting >>> thesis_fusion
Finished <<< thesis_fusion [2.19s]          

Summary: 1 package finished [2.69s]

## Package
- thesis_fusion created (ament_python); deps: rclpy sensor_msgs geometry_msgs std_msgs message_filters visualization_msgs vision_msgs
- colcon build thesis_fusion: PASS (built from ros2_ws/ after the repo-root scan errors below)
- Env bridge: ROS env sourced + venv_yolo site-packages on PYTHONPATH (both py3.10). Confirmed: rclpy + ultralytics coexist in one process, numpy stayed 1.26.4.
- Image->numpy: manual reshape of msg.data (NOT cv_bridge) to avoid the Week-2 OpenCV-4.8/4.9 co-resident ABI trap.

## Errors & solutions (summary)
- zed_msgs not found at `thesis_bringup` (live bring-up): shared ZED Box, package absent from this workspace. Fix: `sudo apt install ros-humble-zed-msgs`.
- colcon build run from the repo root scanned third_party/OpenPCDet, third_party/spconv, venv numpy and errored (distutils / `No module named 'pccm'`). Fix: build from `ros2_ws/`, not the repo root.
- `ros2 run` -> "No executable found": auto-generated setup.py had empty console_scripts. Fix: add `fusion_node = thesis_fusion.fusion_node:main` to entry_points, rebuild, re-source.
- Benign matplotlib "Unable to import Axes3D" warning at startup (ultralytics importing matplotlib); ignored.

## Skeleton run (bag playback)
- 'model loaded' lines in log (must be exactly 1): 1
- paired-callback rate (steady): ~10 Hz (10.35 / 10.11 / 9.89 / 10.15 / 9.94 Hz; LiDAR-limited)
- first-pair decode: image (600, 960, 3) enc='bgra8'; cloud xyz (53649, 3)
- stub Detection3DArray published on /fusion/detections, one per synced pair
  (independent check: `timeout 5 ros2 topic hz /fusion/detections` -- run as its own command, not in $())

## Final state (18:02:52)
- Package builds + node runs on the synced stream: YES
- Model loads exactly once: YES (1 "model loaded" line)
- Synchronizer fires at paired rate: ~10 Hz steady
- Env bridge working in one process: YES (venv_yolo PYTHONPATH + ROS Humble; numpy 1.26.4 held)
- Day 1 outcome: PASS (all Day-1 done-criteria met)
