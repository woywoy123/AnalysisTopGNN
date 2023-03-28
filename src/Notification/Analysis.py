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
            return True 
        return False

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
        string += "> EventGenerator < :: " if self.Event != None else ""
        string += "> GraphGenerator < :: " if self.EventGraph != None else ""
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
        _str = "Tracer not found under: " + Directory
        _str += " please enable either 'DumpPickle' or 'DumpHDF5'." if self.DumpPickle == False and  self.DumpHDF5 == False else ""
        _str += " Regenerating..."
        self.Warning(_str)

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
            root = True if len([l for l in Files[i] if l.endswith(".root")]) > 0 else False
            string = ""
            
            if root and trig:
                string = "!!--- ADDING TO SAMPLE COLLECTION ---"
                self.Success("!!" + "-"*len(string))
                self.Success(string)
                self.Success("!!" + "-"*len(string))
                self.Success("!! -> " + i + " (" + str(len(Files[i])) + ")")
                trig = False
            
            if "DataCache" or "EventCache" in i:
                string = "DataCache" if "DataCache" in i else "EventCache"
                self.Success("!! (" + string + "): " + i)
    
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

    def Finished(self):
        self.Success("Finished Analysis")
