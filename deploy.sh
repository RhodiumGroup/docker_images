docker login -u="$DOCKER_USERNAME" -p="$DOCKER_PASSWORD";
docker push rhodium/worker:$TAG;
docker push rhodium/notebook:$TAG;
