from Functions.Event.Event import EventGenerator
from Functions.GNN.Graphs import GenerateDataLoader
from Functions.IO.IO import PickleObject, UnpickleObject

events = 100
Tree = "nominal"
root_dir = "/CERN/Grid/SignalSamples"

def TestAnomalousStatistics(ev):

    A_D = 0
    A_TM = 0
    A_TM_init = 0
    A_All = 0
    for i in ev.Events:
        Event = ev.Events[i]["nominal"]

        if Event.Anomaly_Detector == True and Event.Anomaly_TruthMatch == True and Event.Anomaly_TruthMatch_init == True: 
            A_All += 1

        if Event.Anomaly_Detector == True: 
            A_D += 1

        if Event.Anomaly_TruthMatch == True: 
            A_TM += 1

        if Event.Anomaly_TruthMatch_init == True: 
            A_TM_init += 1

    print("Number of events considered: " + str(i))
    print("Number of events with Detector, Truth and Truth_init not well matched particles: " + str(A_All) + " " + str(round(100*float(A_All)/float(i), 4)) + "%")
    print("Number of events with Truth not well matched particles: " + str(A_TM) + " " + str(round(100*float(A_TM)/float(i), 4)) + "%")
    print("Number of events with Truth_init not well matched particles: " + str(A_TM_init) + " " + str(round(100*float(A_TM_init)/float(i), 4)) + "%")
    print("Number of events with Detector particles not well matched with Truth particles: " + str(A_D) + " " + str(round(100*float(A_D)/float(i), 4)) + "%")

def TestSignalSingleFile():
    dir = root_dir + "/user.pgadow.310845.MGPy8EG.DAOD_TOPQ1.e7058_s3126_r10724_p3980.bsm4t-21.2.164-1-0-mc16e_output_root/user.pgadow.24765302._000001.output.root"
    
    ev = EventGenerator(dir, DebugThresh = 10, Debug = True)
    ev.SpawnEvents()
    ev.CompileEvent(SingleThread = True)
    TestAnomalousStatistics(ev)

def TestSignalMultipleFile():
    dir = root_dir + "/user.pgadow.310845.MGPy8EG.DAOD_TOPQ1.e7058_s3126_r10724_p3980.bsm4t-21.2.164-1-0-mc16e_output_root/"
    
    ev = EventGenerator(dir)
    ev.SpawnEvents()
    ev.CompileEvent(SingleThread = True, particle = "TruthTops")
    
    for i in ev.Events:
        print(i, ev.Events[i]) 
    

def TestSignalMultipleFile():
    dir = root_dir + "/user.pgadow.310845.MGPy8EG.DAOD_TOPQ1.e7058_s3126_r10724_p3980.bsm4t-21.2.164-1-0-mc16e_output_root/"
    
    ev = EventGenerator(dir)
    ev.SpawnEvents()
    ev.CompileEvent(particle = "TruthTops")
    
    f = ""
    for i in ev.Events:
        if f != ev.EventIndexFileLookup(i):
            f = ev.EventIndexFileLookup(i)
            print(i, ev.Events[i], f) 

def TestSignalDirectory():
    dir = root_dir
    
    ev = EventGenerator(dir)
    ev.SpawnEvents()
    ev.CompileEvent(SingleThread = True, particle = "TruthTops")
    
    for i in ev.Events:
        print(i, ev.Events[i], ev.EventIndexFileLookup(i)) 
