#!/bin/bash 

source ~/.bashrc

cd ~
source ~/anaconda3/etc/profile.d/conda.sh
cd -
conda activate base
conda env remove -n GNN
conda create --name GNN python=3.10 --yes
conda activate GNN

export CUDA_PATH=/usr/local/cuda-11.8
export VERSION=cu118
export TORCH=1.13.0
export MAX_JOBS=12
export CC=gcc-11
export CXX=gcc-11

cd ../
bash setup.sh
