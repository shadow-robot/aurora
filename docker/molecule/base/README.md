This Docker is build based on [this article](http://jpetazzo.github.io/2015/09/03/do-not-use-docker-in-docker-for-ci/).

Giving access to Docker socket will allow to spawn Docker containers outside of existing container

```bash
docker run -v /var/run/docker.sock:/var/run/docker.sock -it docker
```
