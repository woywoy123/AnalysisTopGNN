#!/bin/bash 

export VERSION=${version}
export CUDA=${cuda}
export CC=gcc-${gcc}
export CXX=g++-${gcc}

sudo apt-get install -y ${CC} ${CXX}
if [[ $VERSION == "cu"* ]]
then
        chmod +x ./.github/scripts/cuda_install.sh
        ./.github/scripts/cuda_install.sh 
        echo "CC=/usr/bin/${CC}" >> $GITHUB_ENV
        echo "CXX=/usr/bin/${CXX}" >> $GITHUB_ENV
        echo "CUDA_PATH=/usr/local/cuda-${CUDA}" >> $GITHUB_ENV
fi
TORCH=${torch}
echo "TORCH=${TORCH}" >> $GITHUB_ENV
echo "VERSION=${VERSION}" >> $GITHUB_ENV

pip install torch==${TORCH} --extra-index-url https://download.pytorch.org/whl/${VERSION}
pip install torch_scatter -f https://data.pyg.org/whl/torch-${TORCH}+${VERSION}.html
pip install torch_sparse -f https://data.pyg.org/whl/torch-${TORCH}+${VERSION}.html
pip install torch_cluster -f https://data.pyg.org/whl/torch-${TORCH}+${VERSION}.html

