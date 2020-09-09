#!/bin/bash

set -x

echo "Copy Dask configuration files from pre-load directory into opt/conda/etc/dask/"
mkdir -p /opt/conda/etc/dask
cp --update -r -v /pre-home/config.yaml /opt/conda/etc/dask/

# set credentials for use when starting workers with dask-gateway
python /pre-home/set_gateway_opts.py

sudo rm /pre-home/config.yaml /pre-home/set_gateway_opts.py

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
            echo "Including $bucket in dask-gateway options";
        fi;
    fi;
done



# needed for CLAWPACK to not throw segfaults sometimes
ulimit -s unlimited

# Run extra commands
$@
