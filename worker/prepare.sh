#!/bin/bash

set -x

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

if [ "$GCSFUSE_TOKEN" ]; then
    echo "$GCSFUSE_TOKEN" > /opt/gcsfuse_token.json
    export GOOGLE_APPLICATION_CREDENTIALS="/opt/gcsfuse_token.json"
fi

if [ "$GCSFUSE_BUCKET" ]; then
    echo "Mounting $GCSFUSE_BUCKET to /gcs"
    /usr/bin/gcsfuse --key-file /opt/gcsfuse_token.json $GCSFUSE_BUCKET /gcs

fi
# Run extra commands
$@