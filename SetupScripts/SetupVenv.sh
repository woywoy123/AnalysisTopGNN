#!/bin/bash 

OutputDir="./"

cd $OutputDir
wget https://www.python.org/ftp/python/3.9.7/Python-3.9.7.tgz
tar -xvf Python-3.9.7.tgz
rm Python-3.9.7.tgz 
cd Python-3.9.7
./configure
make
cd ../ 
./Python-3.9.7/python -m venv PythonGNN
rm -r Python-3.9.7

source $OutputDir"/PythonGNN/bin/activate"

# Packages to be installed.
pip install torch==1.12.1+cu116 torchvision==0.13.1+cu116 torchaudio==0.12.1 --extra-index-url https://download.pytorch.org/whl/cu116
pip install torch-scatter torch-sparse torch-cluster torch-spline-conv torch-geometric -f https://data.pyg.org/whl/torch-1.12.0+cu116.html
pip install torchmetrics
pip install matplotlib
pip install networkx[all]
pip install uproot awkward
pip install h5py
pip install mplhep

cd ../
python setup.py install 
