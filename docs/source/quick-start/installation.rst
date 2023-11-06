Installing Analysis-G
=====================

Installing via Github
_____________________

First clone the project into a target directory. 

.. code-block:: console
    :caption: Cloning the Project via Git

    git clone https://github.com/woywoy123/AnalysisG.git

To automate most of the setup, navigate to the **setup-scripts** directory and run the **setup-venv.sh** script.
This will generate a new Python environment called **GNN**, which can be sourced from the shell script **source_this.sh**. 

.. code-block:: console
    :caption: Running the Installation script 

    cd AnalysisG/setup-scripts && bash setup-venv.sh

If you are running the framework on a HPC cluster, for instance **lxplus** or some other Linux environment, make sure to have at least **GCC 6.20** enabled.
For example, on **lxplus** machines, add the following lines to the bashrc file: 

.. code-block:: console
   
    export ATLAS_LOCAL_ROOT_BASE=/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase
    source ${ATLAS_LOCAL_ROOT_BASE}/user/atlasLocalSetup.sh
    lsetup "gcc gcc620_x86_64_slc6"

If making changes to the .bashrc is not desired, simply add an alias to it and point the **source** command to the **setup-scripts** folder as shown below:

.. code-block:: console 

   alias GNN='source <some path to repository>/setup-scripts/source_this.sh

This will create a command called **GNN** and when executed will setup the Analysis environment. 

Installing via PyPI (pip)
_________________________

The framework has also been published to PyPI to simplify the installation process.

.. code-block:: console

   pip install analysisg


Additional Software Setup
_________________________

Analysis-G is partly dependent on **PyC** and can be installed via the command **install_pyc**.
Unlike most **PyTorch** packages, the installation process is rather seemless. 
During the build process, the package will scan for **nvcc** (CUDA compiler), and will install the appropriate **PyTorch** version (CUDA/CPU). 

As mentioned in the introduction page of these docs, modules found in this package are completely written in C++.
If CUDA is available, then the package will also proceed to install the native CUDA kernel implementations. 
This however can be a very long and computationally expensive build process.

Unlike the recommended setup-tools based tutorial provided by **PyTorch**, the installation process utilizes an advanced cmake builder called **scikit-build-core**.
This allows for code modifications to be made without having to repetitively recompile unmodified code and wasting computational resources. 
Once installed, the module can be used via: 

.. code-block:: python 

   import pyc

Install via Command-Line
________________________

.. code-block:: console

   cd torch-extensions
   pip install -v .

Install via Framework
_____________________

.. code-block:: console

   install_pyc
