Multi-Threading
***************

This class is targeted at running operations as parallel as possible with minimal CPU idle time. 
This section will explore how to define and run operations in parallel. 

How to Structure your Function 
______________________________

To run the class, the input function needs to expect an array of n-chunks, and output an array of any length. 
An example function would look like the code below:

.. code-block:: python 

    def function(inpt):
        out = inpt.pop(0)
        for i in inpt:
            # do some operation 
            # e.g summing large list
            out += i
        return [out]

To now execute the function above using multiple threads, instantiate the class and specify the chunks and threads to run. 

.. code-block:: python 

    from AnalysisG.Tools import Threading

    threads = 12
    chunks = 1000
    th = Threading(<some list>, function, threads, chunks)
    th.Start()

    output = sum([i for i in th._list if i is not None])

One might wonder why the ``is not None`` condition is required. 
The threading class will assure that the order of the list is preserved, and this is achieved by creating a list of ``None`` type and injecting the thread results at the associated index. 
From the above example function, the aim was to merge a very large list into a single number, so naturally the list output would incrementally shrink and could potentially cause issues with classes which are expecting a consistent array length. 


Include a Progress Bar to the Threading Function 
________________________________________________

One could also modify the above function and add a progress bar. 
This would slightly degrade performance, but would inform the user how the processing is progressing. 
An example would look like this:

.. code-block:: python

    def function(inpt, _prgbar):
        lock, bar = _prgbar
        out = inpt.pop(0)
        for i in inpt:
            # some operation
            out += i
            with lock: bar.update(1)
        return [out]


Known Issues and Limitations
_____________________________

The above code works just fine on Linux operating systems, however MacOS and Windows might throw errors regarding EOF. 
This is because both operating systems require a ``__main__`` to be defined prior to running any multi-threading instances.
A possible solution would be to implement something like shown below: 

.. code-block:: python

    def function(.....):
        # some operation 
        return []

    def Start_Threads():
        th = Threading(...., function, ..., ...)
        th.Start()

    if __name__ == "__main__":
        Start_Threads()

