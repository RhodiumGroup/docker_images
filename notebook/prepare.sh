#!/bin/bash

set -x

echo "Copy files from pre-load directory into home"
cp --update -r -v /pre-home/. /home/jovyan

if [ -e "/opt/app/environment.yml" ]; then
    echo "environment.yml found. Installing packages"
    /opt/conda/bin/conda env update -f /opt/app/environment.yml
else
    echo "no environment.yml"
fi

if [ "$EXTRA_CONDA_PACKAGES" ]; then
    echo "EXTRA_CONDA_PACKAGES environment variable found.  Installing."
    /opt/conda/bin/conda install $EXTRA_CONDA_PACKAGES
fi

if [ "$EXTRA_PIP_PACKAGES" ]; then
    echo "EXTRA_PIP_PACKAGES environment variable found.  Installing".
    /opt/conda/bin/pip install $EXTRA_PIP_PACKAGES
fi

SA_FILE=~/service-account-credentials.json
if [ ! -f $SA_FILE ]; then
    echo "no credentials file present"
else
    echo "credentials file present...checking to see if bucket mounted"
fi

GCSFUSE_BUCKET=rhg-data
if [ ! -d /gcs/climate ]; then
    echo "Mounting $GCSFUSE_BUCKET to /gcs"
    /usr/bin/gcsfuse --key-file=$SA_FILE $GCSFUSE_BUCKET /gcs
fi

if [ -f ~/worker-template.yml ]; then
    echo "appending service-account-credentials to worker-template"
    python add_service_creds.py
fi

# Run extra commands
$@