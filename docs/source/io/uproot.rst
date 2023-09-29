UpROOT wrapper
**************
This class is predominantly designed to be interfaced with core modules in the framework. 
However, it can be used as a completely standalone module with minimal configuration. 
Part of this module is the so called `MetaData` object. 
This class contains additional information about the input ROOT samples if ``PyAMI`` is enabled. 
If ``PyAMI`` is not installed or authenticated to, then it will try to scrape the ROOT files for additional meta data. 

Functions
_________

- ``InputSamples(input: Union[str, Dict, List])``:
    This function will scan the given input for ROOT files. 
    If the input is a string containing the `.root` extension, then only that file will be used, otherwise it will assume the input is a directory and scan it for possible ROOT files.
    For lists, the function will assume these to be `.root` files and never directories. 
    If the input is a dictionary, then the keys can be interpreted as being directories, with values being either lists of ROOT files to read, or single ROOT file strings.

Attributes
__________

- ``Trees``: 
    Expects a list of strings pointing to the trees to be read.

- ``Branches``: 
    Expects a list of strings pointing to any branches.

- ``Leaves``: 
    Expects a list of strings pointing to any leaves to be read.

- ``ScanKeys``: 
    Will check whether the given `Trees/Branches/Leaves` are found within the ROOT samples.

- ``DisablePyAMI``: 
    Skips ``PyAMI`` meta-data look-ups.


MetaData wrapper
****************
This is a class which wraps the output of ``PyAmi`` when performing a meta-data search on the input samples.
To use this wrapper effectively, you need to authenticate using the ``voms-proxy-init`` command.
Luckily, the framework comes with a pre-built script, which does this for you, simply enter ``AUTH_PYAMI`` into the terminal and it will ask for the ``userkey/usercert.pem`` directories, followed by a password prompt. 
If the user is not authenticated, this step is skipped and the framework will attempt to inspect the sample's available meta-data. 

Attributes From PyAMI with Authentication
_________________________________________

- ``DatasetName``: 
  Name of the ``DAOD`` from which the sample originated from.

- ``nFiles``:
  Number of ``DAOD`` samples constituting the ``Dataset``.

- ``total_events``:
  The total number of events in this ``Dataset``.

- ``short``:
  A shortened version of the ``Dataset`` name.

- ``DAOD``:
  If the event index is matched to the event numbers in the ROOT sample, then the ``DAOD`` of this event will be given.
  Otherwise it will list all ``DAOD`` samples of the events.

- ``cross_section``
  The generated cross section of the sample

- ``Files``:
  The original generation path where the sample was generated in. 

- ``generator_tune``:
  The generator used to produce the ``Dataset``.

- ``keywords``:
  Keywords used to find the sample.

- ``isMC``:
  A Boolean value indicating whether the sample is a Monte Carlo sample

- ``version``:
  The version of the sample (e.g. p-tag)

This is just a subset of attributes, more can be added by modifying the ``self._vars`` attribute of the ``MetaData`` class under ``src/IO/UpROOT.py`` (this is for more advanced users).
