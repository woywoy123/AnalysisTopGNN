The Condor Submission Module
****************************

This module is used to construct chained **Condor** jobs from an analysis script.
Condor is quite a popular high performance clustering batch system used to schedule jobs. 
Usually, jobs are submitted in the form of bash or python scripts, with the condition that these scripts do not require user interaction to execute. 
Although one could simply write an analysis script with the framework, this module has a lot of features which automates parallelism and distributed computing jobs. 


Condor-Dagman
_____________

An extension to the **Condor** batch system, it allows the users to chain specific jobs into a particular order. 
Conceptually this resembles a **Directed Acyclic Graph**, where each job represents a node and the edge direction a job dependenecy.
This system has its own syntax, which is rather simple, but rather tedious to write and implement, since the job's dependency needs to be explicitly resolved and written.
This module aims to streamline this process and introduce the most minimalistic syntax needed to automatically construct job scripts that are readily submitable to a **Condor** batch system.

.. py:class:: Condor

    .. py:method:: AddJob(str job_name, instance, str memory, str time, list[str] waitfor = [])


        Add an Analysis instance to the collection of jobs to run on the HPC cluster.

        :param str job_name: A unique name to give the job.
        :param instance: The **Analysis** object to add to the job collection.
        :param str memory: Requested memory for the job to run (this requires units to be given, e.g. 10MB or 10GB).
        :param str time: Requested time to allocate to the given job (this requires units, e.g. 10min, 10h).
        :param list waitfor: A list of **job_name** strings which this job depends on.

    .. py:method:: LocalRun()

       Execute the current chains locally on the command-line

    .. py:method:: SubmitToCondor()

       Build and submit scripts automatically to the cluster.

    :ivar str OutputDirectory: Globally apply the given output directory to all **Analysis** objects.
    :ivar str ProjectName: Globally apply the given project name to all **Analysis** objects.
    :ivar int Verbose: Globally apply the verbosity to all **Analysis** objects.
    :ivar str PythonVenv: 

       A parameter which selects the python environment to use. 
       In the case of py-venv, simply create an alias or bash environment variable pointing to the particular py-venv directory.
       E.g. PythonGNN=/some-path/py-venv/../activate

    :ivar str CondaVenv: A parameter which selects the conda environment to use by name.


A Simple Illustration of Chained Submissions
____________________________________________

.. code-block:: python

    from some_selection.example import Example
    from some_event.example import EventEx
    from AnalysisG import Analysis

    from AnalysisG.Submission import Condor


    def _template(default=True):
        AnaE = Analysis()
        if default == True:
            AnaE.InputSample("Sample1", smpl + "sample1/" + Files[smpl + "sample1"][0])
            AnaE.InputSample("Sample2", smpl + "sample2/" + Files[smpl + "sample2"][1])
        else:
            AnaE.InputSample(**default)
        AnaE.Threads = 2
        AnaE.Verbose = 1
        return AnaE

    con = Condor()
    con.PythonVenv = "$<some variable>"
    con.ProjectName = "Project"

    # Create some event caches from different ROOT samples
    Ana_1 = _template(
        {"Name": "smpl1", "SampleDirectory": {smpl + "sample2": ["smpl1.root"]}}
    )
    Ana_1.Event = EventEx
    Ana_1.EventCache = True

    Ana_2 = _template(
        {"Name": "smpl2", "SampleDirectory": {smpl + "sample2": ["smpl2.root"]}}
    )
    Ana_2.Event = EventEx
    Ana_2.EventCache = True

    Ana_3 = _template(
        {"Name": "smpl3", "SampleDirectory": {smpl + "sample2": ["smpl3.root"]}}
    )
    Ana_3.Event = EventEx
    Ana_3.EventCache = True

    # Add these to jobs. Notice these do not depend on each other 
    # therefore the waitfor list does not need to be specified.
    con.AddJob("smpl1", Ana_1)
    con.AddJob("smpl2", Ana_2)
    con.AddJob("smpl3", Ana_3)


    # Again create Analysis objects but populate them with selection template objects.
    # Notice the waitfor parameter needs to be set, because these Selections require 
    # EventTemplate like objects, so these jobs are lauched after the events have been cached.
    Ana_s1 = _template({"Name": "smpl1"})
    Ana_s1.EventCache = True
    Ana_s1.AddSelection(Example)
    con.AddJob("example1_1", Ana_s1, waitfor=["smpl1"]) # <- add dependency jobs

    Ana_s2 = _template({"Name": "smpl2"})
    Ana_s2.EventCache = True
    Ana_s2.AddSelection(Example)
    con.AddJob("example1_2", Ana_s2, waitfor=["smpl2"])

    Ana_s3 = _template({"Name": "smpl3"})
    Ana_s3.EventCache = True
    Ana_s3.AddSelection(Example)
    con.AddJob("example1_3", Ana_s3, waitfor=["smpl3"])

    # Run this locally
    con.LocalRun()

    # Submit this to condor
    con.SubmitToCondor()

From the above example, 3 topologically disconnected chains or jobs will be created, one for each ROOT sample.
Also to note, the script does not need to worry about the dependency order, since the module automatically resolves
the dependency tree of jobs.


