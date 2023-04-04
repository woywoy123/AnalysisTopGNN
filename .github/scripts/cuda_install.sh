# Get Ubuntu Release
UBUNTU_V=$(lsb_release -sr)
UBUNTU_V="${UBUNTU_V//.}"

# Prepare installation of CUDA
CPU_ARCH="x86_64"
PIN="cuda-ubuntu${UBUNTU_V}.pin"
PIN_URL="https://developer.download.nvidia.com/compute/cuda/repos/ubuntu${UBUNTU_V}/${CPU_ARCH}/${PIN}"

KEYRING="cuda-keyring_1.0-1_all.deb"
KEYRING_URL="https://developer.download.nvidia.com/compute/cuda/repos/ubuntu${UBUNTU_V}/${CPU_ARCH}/${KERYRING}"

REPO_URL="https://developer.download.nvidia.com/compute/cuda/repos/ubuntu${UBUNTU_V}/${CPU_ARCH}/"

# Get Installer and install keys
wget ${PIN_URL}
sudo mv ${PIN} /etc/apt/preferences.d/cuda-repository-pin-600
wget ${KEYRING} && sudo dpkg -i ${KERYRING} && rm ${KERYRING}
sudo add-apt-repository "deb ${REPO_URL} /"
sudo apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu${UBUNTU_V}/${CPU_ARCH}/3bf863cc.pub
sudo apt-get update

# Install CUDA
sudo apt-get -y install cuda-${CUDA}
