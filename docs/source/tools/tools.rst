Tools and cTools
****************

A set of helper classes that provide the framework with additional tools that otherwise would require writing repetitive code.
Some functions have been ported to C++ to exploit faster multi-threading operations, these will be separately highlighted.

.. py:class:: Tools

    .. py:method:: lsFiles(str directory, extension = None) -> list[str]
        
        A method which returns the file structure of a given path.

        :param str directory: The absolute/relative path to search in. 
        :param str, None extension: Only return files in the specified directory if it matches the given file extension.

    .. py:method:: ls(str directory) -> list[str]

        A method which only returns the specified directory structure (does not search recursively or care about file extensions).

        :param str directory: The absolute/relative path to search in.

    .. py:method:: IsPath(str directory) -> bool

        Checks whether the given directory is a path or if it exists.
        
        :param str directory: The absolute/relative path to check.

    .. py:method:: IsFile(str directory, bool quiet) -> bool

        Checks whether the given directory is a file or if it exists. 

        :param str directory: The absolute/relative path to check.
        :param bool quiet: Disables/Enables any alerting of running the method.

    .. py:method:: ListFilesInDir(str directory, str extension) -> list[str]

        Recursively checks the given path for files with the given extension.

        :param str directory: The absolute/relative path to check.
        :param str extension: The file extension to search the path for.

    .. py:method:: pwd() -> str
        
        Returns current working directory.

    .. py:method:: abs(str directory) -> str

        Converts a relative directory string to an absolute path.

        :param str directory: A relative directory path string.

    .. py:method:: path(str directory) -> str

        Converts the input to a path string.

        :param str directory: The absolute/relative path to convert into a path string.

    .. py:method:: filename(str directory) -> str

        Extracts the filename of the input string.

        :param str directory: The directory/input to convert.

    .. py:method:: mkdir(str directory)

        Creates the given path in the file-system. 
        If the output is a nested directory structure, the entire path structure if will be created.

        :param str directory: The directory path to create on the file-system.

    .. py:method:: rm(str directory)

        Deletes the the specified directory, regardless of the contents!

        :param str directory: The directory path to delete from the file-system.


    .. py:method:: cd(str directory) -> str

        The directory that the Python interpreter should change to. 

        :param str directory: The directory path string.

    .. py:method:: MergeListsInDict(dict inpt) -> list

        Recursively merges lists within the input dictionary, without preserving the keys or dictionary path.

        :param dict inpt: A dictionary with lists values.


    .. py:method:: DictToList(dict inpt) -> list 

        Aims to recrusively merge dictionary content but saves the keys string path, if the input dictionary is nested.

        :param dict inpt: The dictionary to merge into a list.

    .. py:method:: Quantize(list inpt, int size) -> list[list]

        Splits the input list into a nested list, with the nested lists being of specified size.

        :param list inpt: A list of values to split.
        :param int size: The size of each element within the nested list.


    .. py:method:: MergeNestedList(list[list] inpt) -> list

        Does the opposite of Quantize. Given a nested list, the method will attempt to rebuild a continuous single dimensional list.
        
        :param list[list] inpt: A nested list of list to convert.


    .. py:method:: MergeData(ob1, ob2) -> type of ob1 or ob2

        A more abstract merging method. It aims to merge two input data types (list, dict, int, float), into a single entity.
        A simple example would be, if two inputs are dictionaries and each contains different keys, the method will merge the two dictionaries into a single dictionary.
        For a more complex case, consider two dictionaries with mutual keys, but nested lists as values. 
        In such cases, the method will output a single dictionary but the list structure will be preserved, and the contents merged.

        :param list, dict, int, float ob1: The first type to merge.
        :param list, dict, int, float ob2: The second type to merge.


.. py:class:: cTools (import via AnalysisG._cmodules.ctools import CTools)


    .. py:method:: csplit(str val, str delimiter) -> list 

        Splits a given string by the given delimiter. This method is interfaced with C++ using Cython.
    
        :param str val: The string to split.
        :param str delimiter: A sub-string key to split the input by.


    .. py:method:: chash(str inpt) -> str

        Returns a hash of the input string.

        :param str inpt: The string to compute the hash for.

    .. py:method:: cQuantize(list v, int size) -> list[list]

        Does the same as Quantize, but much faster.

        :param list v: The target list to split.
        :param int size: The size of each element within the nested output list.

    .. py:method:: cCheckDifference(list inpt1, list inpt2, int threads) -> list

        Returns a list of differernces between inpt1 and inpt2, using n-CPU threads.

        :param list inpt1: The first list to scan relative to the second list.
        :param list inpt2: The source list to scan against. 
        :param int threads: The number of threads to utilize during the scanning (particularly helpful for large string lists).
