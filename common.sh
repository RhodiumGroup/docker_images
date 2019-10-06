#!/bin/sh

# install apt-get packages
apt-get update -y
apt-get install -yq --no-install-recommends \
  apt-utils \
  bzip2 \
  curl \
  lsb-release \
  gnupg2 \
  sudo

# install gcsfuse, google cloud sdk, kubectl
# (need curl to be installed earlier)
export GCSFUSE_REPO=gcsfuse-`lsb_release -c -s`
echo "deb http://packages.cloud.google.com/apt $GCSFUSE_REPO main" | \
  tee /etc/apt/sources.list.d/gcsfuse.list
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] \
  https://packages.cloud.google.com/apt cloud-sdk main" | \
  tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | \
  apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -
apt-get update -y
apt-get install -yq --no-install-recommends gcsfuse google-cloud-sdk kubectl
alias googlefuse=/usr/bin/gcsfuse

apt-get clean

# get cloud sql proxy
wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O /usr/bin/cloud_sql_proxy
chmod +x /usr/bin/cloud_sql_proxy

# conda updates
conda update -n base conda
conda config --set channel_priority strict

# filepath curating
chmod +x /usr/bin/prepare.sh
mkdir /gcs
mkdir /opt/app
