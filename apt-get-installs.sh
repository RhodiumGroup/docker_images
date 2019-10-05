apt-get update --fix-missing --no-install-recommends

apt-get install -yq --no-install-recommends apt-utils \
    wget bzip2 ca-certificates curl git gnupg2 apt-transport-https

# install google cloud sdk
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] \
  https://packages.cloud.google.com/apt cloud-sdk main" | \
  sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | \
  sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -
apt-get update -y
apt-get install google-cloud-sdk kubectl -y

# install gcsFUSE
export GCSFUSE_REPO=gcsfuse-`lsb_release -c -s`
echo "deb http://packages.cloud.google.com/apt $GCSFUSE_REPO main" | tee /etc/apt/sources.list.d/gcsfuse.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
apt-get update -y
apt-get install gcsfuse -y
alias googlefuse=/usr/bin/gcsfuse

apt-get upgrade -yq --no-install-recommends

apt-get clean
