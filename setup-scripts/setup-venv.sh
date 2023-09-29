#!/bin/bash 

export ATLAS_LOCAL_ROOT_BASE=/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase
source ${ATLAS_LOCAL_ROOT_BASE}/user/atlasLocalSetup.sh
Version="3.9"
lsetup "gcc gcc620_x86_64_slc6"
lsetup "python $Version.14-x86_64-centos7"
python$Version -m venv PythonGNN
source ./PythonGNN/bin/activate

echo "#!/bin/bash" > source_this.sh
echo "export ATLAS_LOCAL_ROOT_BASE=/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase" >> source_this.sh
echo 'source ${ATLAS_LOCAL_ROOT_BASE}/user/atlasLocalSetup.sh' >> source_this.sh
echo 'lsetup "gcc gcc620_x86_64_slc6"' >> source_this.sh
echo "export PythonGNN=$PWD/PythonGNN/bin/activate" >> source_this.sh
echo "alias GNN='source $PWD/PythonGNN/bin/activate'" >> source_this.sh
echo 'source $PythonGNN' >> source_this.sh

source ./source_this.sh
cd ../
pip install --no-cache-dir -v .
CONFIG_PYAMI
CHECK_CUDA
POST_INSTALL_PYC


