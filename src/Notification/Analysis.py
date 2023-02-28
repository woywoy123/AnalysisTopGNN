from .Notification import Notification
import time

class Analysis(Notification):

    def __init__(self):
        pass

    def EmptyDirectoryWarning(self, Directory):
        pass
    
    def NoSamples(self, SampleMap, name):
        if len(SampleMap) == 0:
            self.Failure("No ROOT samples were found in: " + name)
    
    def NothingToIterate(self):
        self.Failure("No samples loaded.")
    
    def EventImplementationCommit(self):
        if self.Event == None:
            return 
        Event = self.CopyInstance(self.Event)

        if Event._CommitHash:
            msg = "!!>> Identified commit of Event Implementation: " + Event._CommitHash
            msg += " <<" + " (Deprecated)" if Event._Deprecated else ""
            self.Success("-"*len(msg))
            self.Success(msg) 
            self.Success("-"*len(msg))

    def EmptySampleList(self):
        if len(self) == 0:
            string = "No samples found in cache. Exiting..."
            self.Failure("="*len(string))
            self.FailureExit(string)
   
    def StartingAnalysis(self):
        string1 = "---" + " Starting Project: " + self.ProjectName + " ---"

        string = ""
        string += "> EventGenerator < :: " if self.EventCache and self.Event != None else ""
        string += "> GraphGenerator < :: " if self.DataCache and self.EventGraph != None else ""
        string += "> TrainingSampleGenerator < :: " if self.TrainingSampleName else ""
        string += "> Optimization < :: " if self.Model != None else ""
        string += "> ModelEvaluator < :: " if len(self._ModelDirectories) != 0 or self.PlotNodeStatistics else ""
        string += "> Selections < :: " if len(self._Selection) != 0 else ""
        string += "> Merging Selections < :: " if len(self._MSelection) != 0 else ""
        
        l = len(string) if len(string1) < len(string) else len(string1)
        self.Success("="*l)
        self.Success(string1)
        self.Success(string)
        self.Success("="*l)

    def NoCache(self, Directory):
        self.Warning("No cache was found under " + Directory)

    def MissingTracer(self, Directory):
        self.Warning("Tracer not found under: " + Directory + " please enable either 'DumpPickle' or 'DumpHDF5'")

    def NoEventImplementation(self):
        ex = "Or do: from AnalysisTopGNN.Events import Event"
        self.Failure("="*len(ex))
        self.Failure("No Event Implementation Provided.")
        self.Failure("See src/EventTemplates/Event.py")
        self.Failure(ex)
        self.Failure("="*len(ex))
        self.FailureExit("Exiting...")
    
    def NoEventGraphImplementation(self):
        message = "EventGraph not defined (obj.EventGraph). See implementations (See src/Events/EventGraphs.py)"
        self.Failure("="*len(message))
    
    def ReadingFileDirectory(self, f):
        self.Success("!!Reading Files in Directory '" + f + "':")
        return f

    def FoundFiles(self, Files):
        if len(Files) == 0:
            return 
        trig = True 
        for i in Files:
            root = False
            for k in Files[i]:
                if k.endswith(".root"):
                    root = True 
                    break 
            
            string = ""
            if root and trig:
                string = "!!--- ADDING TO SAMPLE COLLECTION ---"
            if "DataCache" in i and trig:
                string = "!!--- FOUND DATA CACHE ---"
            if "EventCache" in i and trig:
                string = "!!--- FOUND EVENT CACHE ---"

            if trig:
                self.Success("!!" + "-"*len(string))
                self.Success(string)
                self.Success("!!" + "-"*len(string))
                trig = False
            self.Success("!!-> " + i + " (" + str(len(Files[i])) + ")")
    
    def CantGenerateTrainingSample(self):
        string = "Can't generate training sample, please choose either 'EventCache' or 'DataCache'"
        self.Failure("="*len(string))
        self.FailureExit(string)

    def FileNotFoundWarning(self, Directory, Name):
        pass

    def CheckPercentage(self):
        gr = False
        if self.TrainingPercentage > 100:
            self.TrainingPercentage = 80
            gr = "greater than 100%"
        if self.TrainingPercentage <= 0:
            self.TrainingPercentage = 80
            gr = "less than 0%"
        
        if gr:
            self.Warning("Specified Training Percentage " + gr + ". Setting to 80%")

    def ModelNameAlreadyPresent(self, Name):
        self.Warning("Model Name already exists. Skipping...")

    def InvalidOrEmptyModelDirectory(self):
        self.Warning("Given model directory is empty or invalid. Skipping...")
    
    def AddedSelection(self, Name):
        self.Success("Added Selection (" + Name +") to Analysis. The output will be within the project folder under 'Selections/" + Name + "'.")

    def __CheckSettings(self):
        inv = self.CheckSettings()
        if len(inv) == 0:
            return 
        self.Warning("Found the following invalid settings: " + "\n".join(inv))
        time.sleep(5)
