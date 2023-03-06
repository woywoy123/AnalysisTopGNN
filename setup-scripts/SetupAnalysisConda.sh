#!/bin/bash 

source ~/.bashrc

cd ~
source ~/anaconda3/etc/profile.d/conda.sh
cd -
conda activate base
conda env remove -n GNN
conda create --name GNN python=3.10 --yes
conda activate GNN

conda install --yes -c conda-forge root
conda install --yes pip

conda install --yes pytorch torchvision torchaudio pytorch-cuda=11.7 -c pytorch -c nvidia
conda install --yes -c conda-forge torchmetrics
conda install --yes matplotlib
conda install --yes pyg -c pyg

pip install networkx[all]
pip install uproot awkward
pip install h5py
pip install mplhep
pip install Cython
pip install vector

cd ../
pip install .

cd torch-extensions
pip install .
