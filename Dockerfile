# 1. Specify the base image
FROM arm64v8/ros:humble-ros-base

# 2. Update package lists and install all necessary tools
RUN apt-get update && apt-get install -y \
    # ROS2 Python build tools
    ros-humble-camera-ros \
    v4l-utils \
    python3-colcon-common-extensions \
    python3-rosdep \
    python3-pip \
    python3-serial
    # Camera and OpenCV tools
    v4l-utils \
    ros-humble-cv-bridge \
    # C++ Development tools
    build-essential \
    cmake \
    gdb \
    # Text editor and utilities
    neovim \
    git \
    && rm -rf /var/lib/apt/lists/*

# 3. Set the default working directory
WORKDIR /ssl_ws

# 4. Automatically source ROS2 and set Neovim as default editor
RUN echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
RUN echo "export EDITOR=nvim" >> ~/.bashrc
