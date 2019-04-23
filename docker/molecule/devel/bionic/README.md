## Launching container with UI

In order to launch development image please use the following command

```bash
docker run -it --name sample_dev -e DISPLAY -e QT_X11_NO_MITSHM=1 -e LOCAL_USER_ID=$(id -u) \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v /tmp/.X11-unix:/tmp/.X11-unix:rw shadowrobot/aurora-molecule-devel:bionic
```
