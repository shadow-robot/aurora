#!/usr/bin/env bash
set -e
BASE_IMAGE="registry"
REGISTRY="shadowrobot"
IMAGE="$REGISTRY/$BASE_IMAGE"
CID=$(docker ps | grep $IMAGE | awk '{print $1}')
docker pull $IMAGE

LATEST=`docker inspect --format "{{.Id}}" $IMAGE`
RUNNING=`docker inspect --format "{{.Image}}" $CID`
NAME=`docker inspect --format '{{.Name}}' $CID | sed "s/\///g"`
echo "Latest:" $LATEST
echo "Running:" $RUNNING
if [ "$RUNNING" != "$LATEST" ];then
    echo "upgrading $NAME"
    //prompt
    stop docker-$NAME
    docker rm -f $NAME
    start docker-$NAME
else
    echo "$NAME up to date"
fi
