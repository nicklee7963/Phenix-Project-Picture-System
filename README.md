# Phenix Project --picture system

## 2026/07/11: camera setup /docker container
1. tailscale to connect rpi 
2. create docker container (my_ros2_camera)
```python
docker run -it \
  --privileged \
  --ipc=host \
  --net=host \
  -v /dev:/dev \
  -v /run/udev:/run/udev:ro \
  -v /usr/share/libcamera:/usr/share/libcamera:ro \
  -v ~/ssl_ws:/ssl_ws \
  --name my_ros2_camera \
  rpi_ros2_cam:v1 /bin/bash
```

3. simple ros2 package --press tag name to take picture

**Package:** `snapshot_interfaces`
**Service:** `TakePhoto.srv`
**Request** `string label`
**Response:** `bool success`, `string filepath`, `int32 width`, `int32 height`
- **Three nodes**
	1. `camera_ros`(publisher): publish image in a constant frequency -> `/camera/image_raw`
	- `ros2 run camera_ros camera_node`
	2. `camera_server`(server): subscriber to `/camera/image_raw` save image
	- `ros2 run camera_snapshot_pkg server`
	3. `camera_client`(client): wait for user to click enter

