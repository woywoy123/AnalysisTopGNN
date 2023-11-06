.. _meta-data:

MetaData Wrapper
****************

.. py:class:: MetaData

    This is a class which wraps the output of ``PyAmi`` when performing a meta-data search on the input samples.
    To use this wrapper effectively, you need to authenticate using the ``voms-proxy-init`` command.
    Luckily, the framework comes with a pre-built script, which does this for you, simply enter ``auth_pyami`` into the terminal and it will ask for the ``userkey/usercert.pem`` directories, followed by a password prompt. 
    If the user is not authenticated, this step is skipped and the framework will attempt to inspect the sample's available meta-data. 
   
    :param str file: The input path of the file.
    :param bool scan_ami: A switch which enables/disables the meta scanning.
    :param str sampletype: An option which narrows down the DAOD sample search to a specific group.

    .. py:method:: IndexToSample(int index) -> str

        :param int index: Returns the xAOD or filename of the specified event index.

    .. py:method:: ProcessKeys(dict val) -> None

        :param dict val: The keys to search within the ROOT sample.


    :ivar list Trees: Expects a list of strings pointing to the trees to be read.
    :ivar list Branches: Expects a list of strings pointing to the branches to be read.
    :ivar list Leaves: Expects a list of strings pointing to any leaves to be read.
    :ivar str original_input: Returns the original file name, i.e. file.
    :ivar int dsid: Returns the dsid of the data set matched to this ROOT file.
    :ivar str amitag: Returns the amitag of the same being used, this can be retrieved within the sample's metadata.
    :ivar str generators: Returns the generator which produced this sample.
    :ivar bool isMC: Returns a boolean to indicate whether the sample is Monte Carlo
    :ivar str derivationFormat:
    :ivar int eventNumber:
    :ivar float ecmEnergy:
    :ivar float genFiltEff:
    :ivar float completion:
    :ivar float beam_energy:
    :ivar float crossSection:
    :ivar float crossSection_mean:
    :ivar float totalSize: Returns the total file size (memory)
    :ivar int nFiles: Returns the number of files within this sample set
    :ivar int run_number:
    :ivar int totalEvents:
    :ivar int datasetNumber:
    :ivar str identifier:
    :ivar str prodsysStatus:
    :ivar str dataType:
    :ivar str version:
    :ivar str PDF:
    :ivar str AtlasRelease:
    :ivar str principalPhysicsGroup:
    :ivar str physicsShort:
    :ivar str generatorName:
    :ivar str geometryVersion:
    :ivar str conditionsTag:
    :ivar str generatorTune:
    :ivar str amiStatus:
    :ivar str beamType:
    :ivar str productionStep:
    :ivar str projectName:
    :ivar str statsAlgorithm:
    :ivar str genFilterNames:
    :ivar str file_type:
    :ivar str DatasetName:
    :ivar int event_index:
    :ivar str original_name:
    :ivar str original_path:
    :ivar str hash:
    :ivar list keywords:
    :ivar list weights:
    :ivar list keyword:
    :ivar bool found:
    :ivar dict config:
    :ivar dict GetLengthTrees:
    :ivar list MissingTrees:
    :ivar list MissingBranches:
    :ivar list MissingLeaves:
    :ivar list DAODList:
    :ivar dict Files:
    :ivar str DAO:
    :ivar dict fileGUID:
    :ivar dict events:
    :ivar dict fileSize:
    :ivar str sample_name:
    :ivar str logicalDatasetName:


UpROOT wrapper
**************

.. py:class:: UpROOT

    This class is predominantly designed to be interfaced with core modules in the framework. 
    However, it can be used as a completely standalone module with minimal configuration. 
    Part of this module is the so called `MetaData` object. 
    This class contains additional information about the input ROOT samples if ``PyAMI`` is enabled. 
    If ``PyAMI`` is not installed or authenticated to, then it will try to scrape the ROOT files for additional meta data. 


    :param Union[list, dict, str, None] ROOTFiles: Input samples
    :param Union[None, EventGenerator] EventGenerator: A switch which enables/disables the meta scanning.

    .. py:method:: GetAmiMeta() -> MetaData

    .. py:method:: ScanKeys()

        A function which scans the keys within the sample recursively and matches them with the input values.

    .. py:method:: InputSamples(input)

        This function will scan the given input for ROOT files. 
        If the input is a string containing the `.root` extension, then only that file will be used, otherwise it will assume the input is a directory and scan it for possible ROOT files.
        For lists, the function will assume these to be `.root` files and never directories. 
        If the input is a dictionary, then the keys can be interpreted as being directories, with values being either lists of ROOT files to read, or single ROOT file strings.

        :param Union[str, Dict, List] input: The input samples to use.

    :ivar int Verbose: Changes the verbosity of the key scannig and sample detection.
    :ivar int StepSize: Changes the cache step size within **uproot**. 
    :ivar int Threads: Sets the number of threads to utilize during the scanning process.
    :ivar list Trees: Trees to retrieve from the ROOT sample.
    :ivar list Branches: Branches to retrieve and match for the given trees.
    :ivar list Leaves: Leaves to retrieve and match for the given trees and branches.
    :ivar dict Files:
    :ivar bool EnablePyAMI: Enable or disable MetaData.

       
