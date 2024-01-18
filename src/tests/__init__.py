from awtube.awtube import AWTube

path = './gbc_ros2_driver/gbc_ros2_driver/awtube.json'
awtube = AWTube("192.168.12.58", "9001", config_path=path, blocking=False)
