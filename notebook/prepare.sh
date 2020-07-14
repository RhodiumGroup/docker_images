#!/bin/bash

set -x

echo "Copy Dask configuration files from pre-load directory into home/.config"
mkdir -p /home/jovyan/.config/dask
cp --update -r -v /pre-home/config.yaml /home/jovyan/.config/dask/

# should probably pick one of these!!! The second is new, but is implied by the
# cp /pre-home below, and we actually only read the version in ~ in rhg_compute_tools.
cp -r -v /pre-home/worker-template.yml /home/jovyan/.config/dask/
cp -r -v /pre-home/worker-template.yml /home/jovyan/

sudo rm /pre-home/config.yaml

echo "Copy files from pre-load directory into home"
cp --update -r -v /pre-home/. /home/jovyan

# mirror directory used on workers
sudo mkdir -p /opt/gcsfuse_tokens/
mkdir -p /home/jovyan/service-account-credentials/
sudo cp /home/jovyan/service-account-credentials/*.json /opt/gcsfuse_tokens/

for f in /home/jovyan/service-account-credentials/*.json;
do
    # check to make sure we're matching a file, not literally '../*.json'
    if [[ -f "$f" ]]; then
        bucket=$(basename ${f/.json/});
        if ! grep -q "/gcs/${bucket}" /proc/mounts; then
            echo "Mounting $bucket to /gcs/${bucket}";
            mkdir -p "/gcs/$bucket";
            /usr/bin/gcsfuse --key-file="$f" "$bucket" "/gcs/${bucket}";
        fi;
    fi;
done

if [ -f "/home/jovyan/worker-template.yml" ]; then
    echo "appending service-account-credentials to worker-template";
    python /home/jovyan/add_service_creds.py;
fi

# Run extra commands
$@
