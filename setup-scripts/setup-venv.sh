#!/bin/bash 

export ATLAS_LOCAL_ROOT_BASE=/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase
source ${ATLAS_LOCAL_ROOT_BASE}/user/atlasLocalSetup.sh
Version="3.11"
python$Version -m venv PythonGNN
source ./PythonGNN/bin/activate

echo "#!/bin/bash" > source_this.sh
echo "export PythonGNN=$PWD/PythonGNN/bin/activate" >> source_this.sh
echo "alias GNN='source $PWD/PythonGNN/bin/activate'" >> source_this.sh
echo 'source $PythonGNN' >> source_this.sh

