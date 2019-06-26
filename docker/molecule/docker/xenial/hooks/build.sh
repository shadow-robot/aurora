#!/usr/bin/env bash

export DOCKERFILE_PATH=${DOCKERFILE_PATH:-Dockerfile}

echo "docker build --build-arg aurora_branch=$SOURCE_BRANCH -f $DOCKERFILE_PATH -t $IMAGE_NAME ."
echo "SOURCE_BRANCH => $SOURCE_BRANCH"
echo "aurora_branch => $aurora_branch"


docker build --build-arg ml_docker_aurora_branch="${SOURCE_BRANCH}" -f "${DOCKERFILE_PATH}" -t "${IMAGE_NAME}" .

# docker build --build-arg CUSTOM=$VAR -f $DOCKERFILE_PATH -t $IMAGE_NAME .
