## Molecule Dockers

Molecule docker images were created based on [this article](http://jpetazzo.github.io/2015/09/03/do-not-use-docker-in-docker-for-ci/).
Giving access to Docker socket will allow to spawn Docker containers outside of existing container.
So instead of running Docker inside Docker it is running them in parallel on host.

Please check example how to correctly launch such configuration:

```bash
docker run -v /var/run/docker.sock:/var/run/docker.sock -it docker
```
