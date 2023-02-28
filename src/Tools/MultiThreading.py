import multiprocessing
import torch.multiprocessing
torch.multiprocessing.set_sharing_strategy("file_system")
from torch.multiprocessing import Process, Pipe
import math
import gc
from AnalysisTopGNN.Notification import MultiThreading
from tqdm import tqdm

class TemplateThreading:

    def __init__(self, function, val, index):
        self._v = val
        self._f = function
        self._i = index
        self.i = None
        self.lock = None
        self.started = False
    
    def Runner(self, q):
        _l = list(self._f.__code__.co_varnames)[:2]
        _l_ = {_l[0] : self._v} 
        if "_prgbar" in _l:
            with self.lock:
                bar = tqdm(
                        desc = f'MultiThreading {self.i}', total = len(self._v), 
                        position = self.i, leave = False, 
                        colour = "GREEN", dynamic_ncols = True)
            _l_["_prgbar"] = (self.lock, bar)
        _r = self._f(**_l_)
        if "_prgbar" in _l:
            with self.lock:
                bar.close()

        for i in self._v:
            del i
        try:
            q.send(_r)
            for i in _r:
                del i 
        except:
            q.send(False)

    def MainThread(self):
        r = self._f(self._v) 
        for i in self._v:
            del i
        return r


class Threading(MultiThreading):
    def __init__(self, lists, Function, threads = 12, chnk_size = None):
        self._threads = threads
        self._lists = lists
        self._function = Function
        self.Caller = "MULTITHREADING"
        self.Title = "TOTAL JOB PROGRESS"
        self.VerboseLevel = 3
        
        self.AlertOnEmptyList()
        if chnk_size != None:
            _quant = int(len(lists)/chnk_size)+1
        else:
            _quant = self._threads
        
        cpu_ev = math.ceil(len(self._lists) / _quant)
        if cpu_ev == 0:
            cpu_ev = 1
        self._chnk = [self._lists[i : i+cpu_ev] for i in range(0, len(self._lists), cpu_ev)]
        self._indx = [[i, i + cpu_ev] for i in range(0, len(self._lists), cpu_ev)]
        self._lists = [i for i in range(len(self._lists))]
    
    def Start(self):
        if self._lock:
            return 
        it = 1
        tmp = 0
        
        lock = torch.multiprocessing.Manager().Lock()
        with lock:
            bar = tqdm(
                    desc = self.Title, total = len(self._chnk), 
                    position = 0, leave = None, 
                    colour = "GREEN", dynamic_ncols = True)

        for i in range(len(self._chnk)):
            recv, send = Pipe(False)
            T = TemplateThreading(self._function, self._chnk[i], self._indx[i])
            T.i = (i)%self._threads +1
            T.lock = torch.multiprocessing.Manager().Lock()
            P = Process(target = T.Runner, args = (send, ))
            self._chnk[i] = [P, recv, T]

        for i in range(len(self._chnk)):
            self.CheckJobs(i, (lock, bar))

        gc.collect()
        with lock:
            bar.close()

    def CheckJobs(self, t, lks):
        lock, bar = lks

        for k in range(self._threads):
            if k+t == len(self._chnk):
                break
            i = self._chnk[t+k]
            if i == None:
                t += 1
                continue
            if i[2].started == True:
                continue
            i[0].start()
            i[2].started = True

        i = self._chnk[t]    
        try:
            out = i[1].recv()
            self._chnk[t]
        except:
            i[0].terminate()
            out = False
            self.RecoveredThread(i[2].i)
        indx = i[2]._i
        
        if out == False:
            out = i[2].MainThread()
        for j, d in zip(range(indx[0], indx[1]), out):
            self._lists[j] = d

        with lock:
            bar.update(1)

        del self._chnk[t][2]
        del self._chnk[t][1]
        del self._chnk[t][0]
        self._chnk[t] = None
