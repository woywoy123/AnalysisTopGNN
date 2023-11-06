Using nTupler After Running a Selection
***************************************

Introduction
____________
The idea behind using the nTupler class is to automate the process of outputting ROOT ntuples, which can be further processed upstream, to something like a dedicated fitting tool. 
Once a Selection implementation has completed, ``HDF5`` files will be generated within the Project's ``Selections/<selection name>`` path.
To access the content of these HDF5 files, the nTupler class is required, since it handles all the IO details regarding ROOT and the SelectionTemplate class. 
In principle the HDF5 content can be merged into a single object, thus restoring the original state of the selection implementation, but this could be rather slow and computationally expensive, since the backend would need to merge all selection events.


.. py:class:: nTupler

    .. py:method:: This(str var_path, str tree)

        A method used to point the class to the selection-name and its associated 
        attribute path to the particular selection tree.
        
        :params str var_path: Below is a summary of the syntax expected for this variable:
        
            - If the entire object is to be retrieved, simply append a "``->``" to the selection, e.g.
                ``SelectionName ->``

            - If the attribute to be read is a dictionary, then use the synatx;  
                ``SelectionName -> Attribute -> key1 -> key2 -> ...``

            - If the attribute is a list, then only point to the attribute; 
                ``SelectionName -> Attribute``

        :params str tree: The specific ROOT tree to point the class to.

    .. py:method:: merged() -> dict[str, SelectionTemplate]

        This function allows for post selection output to be merged into a single object.
        During the execution of the **Selection** implementation, multiple threads are spawned, 
        which individually save the output of each event selection, meaning a lot of files being written and making 
        it less ideal for inspecting the data.
        As such, ``.hdf5`` files associated with the particular **SelectionTemplate** are merged into single object.

    .. py:method:: MakeROOT(str output) -> None

        A function which dumps the instruction variables given to **This** to a ROOT file 

        :param str output: The output path and filename to store the selections.

    :ivar int Threads: Number of CPU cores to use when merging ``.hdf5`` samples.
    :ivar int Chunks: Number of events to assign to a given thread after each job. 
    :ivar str ProjectName:
        **Important Parameter**: This parameter points the class to the workspace.
        If the **SelectionTemplate** was generated with some **ProjectName** from the Analysis object, 
        then apply the same name to this parameter.



Example Code Usage
__________________

.. code-block:: python 

   ntuple = nTupler()
   ntuple.ProjectName = "ProjectName" # <- important parameter
   ntuple.This("SelectionName ->", "Tree")
   ntuple.This("SelectionName -> somevar", "Tree2")
   # ..... 

   ntuple.MakeROOT("Somepath/some_root_file")


   # Converting the HDF5 back into the orignal object
   SelObj = ntuple.merged()

    # Or iterate over the file event by event 
    for i in ntuple:
        print(i) # SelObj @ event 
        print(i.hash)
