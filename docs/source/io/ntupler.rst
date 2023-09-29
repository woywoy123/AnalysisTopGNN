Using nTupler After Running a Selection
***************************************

Introduction
____________
The idea behind using the nTupler class is to automate the process of outputting ROOT ntuples, which can be further processed upstream, to something like a dedicated fitting tool. 
Once a Selection implementation has completed, ``HDF5`` files will be generated within the Project's ``Selections/<selection name>`` path.
To access the content of these HDF5 files, the nTupler class is required, since it handles all the IO details regarding ROOT and the SelectionTemplate class. 
In principle the HDF5 content can be merged into a single object, thus restoring the original state of the selection implementation, but this could be rather slow and computationally expensive, since the backend would need to merge all selection events.

Functions and Attributes
________________________

- ``InputSelection(path)``:
  This function expects a path string, which points to the folder containing the HDF5 files. See the example code later in this tutorial. 

- ``This(path, tree)``:
  Read this selection (path) from this tree. 
  The path input has the following syntax: 

  - If the entire object is to be retrieved, simply append a "``->``" to the selection, e.g.
        ``SelectionName ->``. 
  - If the attribute to be read is a dictionary, then use the synatx;  
        ``SelectionName -> Attribute -> key1 -> key2 -> ...``.
  - If the attribute is a list, then only point to the attribute; 
        ``SelectionName -> Attribute``.

- ``merged() -> {Tree: SelectionObject}``:
  Merges ``.hdf5`` files into a single Selection object representing the cummulative results of the ``SelectionName``.

- ``Threads``: 
  Number of CPU cores to use when merging ``.hdf5`` files.

- ``chnk``:
  Number of events to assign to a given thread after each job. 

Example Code Usage:
___________________

.. code-block:: python 

   ntuple = nTupler()
   ntuple.InputSelection("PathToProjectFolder/ProjectName/Selections/SelectionName")
   ntuple.This("SelectionName ->", "Tree")

   # Converting the HDF5 back into the orignal object
   SelObj = ntuple.merged()

    # Or iterate over the file event by event 
    for i in ntuple:
        print(i) # SelObj @ event 
        print(i.hash)
