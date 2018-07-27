#!/bin/bash

set -x

echo "Copy files from pre-load directory into home"
cp --update -r -v /pre-home/. /home/jovyan

if [[ -e "/opt/app/environment.yml" ]]; then
    echo "environment.yml found. Installing packages";
    /opt/conda/bin/conda env update -f /opt/app/environment.yml;
else
    echo "no environment.yml";
fi

if [[ "$EXTRA_CONDA_PACKAGES" ]]; then
    echo "EXTRA_CONDA_PACKAGES environment variable found.  Installing.";
    /opt/conda/bin/conda install $EXTRA_CONDA_PACKAGES;
fi

if [[ "$EXTRA_PIP_PACKAGES" ]]; then
    echo "EXTRA_PIP_PACKAGES environment variable found.  Installing".;
    /opt/conda/bin/pip install $EXTRA_PIP_PACKAGES;
fi

if [[ -e "/home/jovyan/conda_environment.yml" ]]; then
    echo "installing conda env";
    /opt/conda/bin/conda env create -f /home/jovyan/conda_environment.yml;
fi

SA_FILE=/home/jovyan/service-account-credentials.json
if [[ ! -f $SA_FILE ]]; then
    echo "no credentials file present";
else

    GCSFUSE_BUCKET=rhg-data
    if ! grep -q "/gcs" /proc/mounts; then
        echo "Mounting $GCSFUSE_BUCKET to /gcs";
        /usr/bin/gcsfuse --key-file=$SA_FILE $GCSFUSE_BUCKET /gcs;
    fi

    if [[ -f "/home/jovyan/worker-template.yml" ]]; then
        echo "appending service-account-credentials to worker-template";
        python /home/jovyan/add_service_creds.py;
    fi
fi

# Run extra commands
$@
