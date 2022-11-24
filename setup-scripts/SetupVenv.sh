#!/bin/bash 

export ATLAS_LOCAL_ROOT_BASE=/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase
source ${ATLAS_LOCAL_ROOT_BASE}/user/atlasLocalSetup.sh
lsetup "gcc gcc620_x86_64_slc6"
lsetup "python 3.9.14-x86_64-centos7"
python3 -m venv PythonGNN
source ./PythonGNN/bin/activate
#
#export CXX=g++-6.2
#export CC=gcc-6.2
#export LD=g++-6.2
 
# Packages to be installed.
pip3 install matplotlib  
pip3 install networkx[all]
pip3 install uproot awkward
pip3 install h5py
pip3 install mplhep
pip3 install -U scikit-learn

pip3 install torch==1.12.1+cu116 torchvision==0.13.1+cu116 torchaudio==0.12.1 --extra-index-url https://download.pytorch.org/whl/cu116
pip3 install torchmetric
pip3 install torch-scatter -f https://data.pyg.org/whl/torch-1.12.1+cu116.html
pip3 install torch-sparse -f https://data.pyg.org/whl/torch-1.12.1+cu116.html
pip3 install torch-cluster -f https://data.pyg.org/whl/torch-1.12.1+cu116.html
pip3 install torch-spline-conv -f https://data.pyg.org/whl/torch-1.12.1+cu116.html
pip3 install torch-geometric -f https://data.pyg.org/whl/torch-1.12.1+cu116.html

cd ../
python setup.py install

echo "export PythonGNN=$PWD/setup-scripts/PythonGNN/bin/activate" >> ~/.bashrc

