#!/bin/bash 

# Hardcoded parameters
export CUDA=11.8
export CPU_ARCH="x86_64"
export KEYRING="cuda-keyring_1.0-1_all.deb"

# Dynamic Parameters
export UBUNTU_V="$(echo $(lsb_release -sr) | tr -d .)"
export PIN="cuda-ubuntu${UBUNTU_V}.pin"
export PIN_URL="https://developer.download.nvidia.com/compute/cuda/repos/ubuntu$UBUNTU_V/$CPU_ARCH/$PIN"
export KEYRING_URL="https://developer.download.nvidia.com/compute/cuda/repos/ubuntu$UBUNTU_V/$CPU_ARCH/$KEYRING"
export REPO_URL="https://developer.download.nvidia.com/compute/cuda/repos/ubuntu$UBUNTU_V/$CPU_ARCH/"

wget $PIN_URL
mv $PIN /etc/apt/preferences.d/cuda-repository-pin-600
wget $KEYRING_URL && dpkg -i $KEYRING && rm $KEYRING
add-apt-repository "deb $REPO_URL /"
apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu$UBUNTU_V/$CPU_ARCH/3bf863cc.pub
apt-get update

apt-get -y install cuda-$CUDA
