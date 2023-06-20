from AnalysisG.Notification import _MultiThreading
import torch.multiprocessing
from torch.multiprocessing import Process, Pipe

torch.multiprocessing.set_sharing_strategy("file_system")
import multiprocessing
from tqdm import tqdm
import math
from typing import Union


class TemplateThreading:
    def __init__(self, function):
        self._f = function
        self._i = None
        self.i = None
        self.lock = None
        self.started = False
        self._q = None
        self._dct = {}

    def _Prg(self):
        _l = list(self._f.__code__.co_varnames)[:2]
        if "_prgbar" not in _l:
            return {_l[0]: None}

        self._dct["desc"] = f"MultiThreading {self.i}"
        self._dct["position"] = self.i
        self._dct["leave"] = False
        self._dct["colour"] = "GREEN"
        self._dct["dynamic_ncols"] = True
        with self.lock:
            bar = tqdm(**self._dct)

        return {_l[0]: None, "_prgbar": (self.lock, bar)}

    def _Prc(self, _v):
        self._dct["total"] = len(_v)
        _l = self._Prg()
        _l[list(_l)[0]] = _v

        _r = self._f(**_l)

        if "_prgbar" not in _l:
            return _r
        lock, bar = _l["_prgbar"]
        with lock:
            bar.close()
        return _r

    def Exec(self, q):
        while True:
            _v = q.recv()
            if _v == True:
                q.close()
                break

            try:
                q.send(self._Prc(_v))
            except:
                q.send(False)

            for i in _v:
                del i
        del self

    def MainThread(self):
        return self._Prc(self._i[1])

    def Purge(self):
        for i in self._i:
            for j in i:
                del j


class Threading(_MultiThreading):
    def __init__(
        self,
        lists: Union[list],
        Function,
        threads: Union[int] = 12,
        chnk_size: Union[int, None] = None,
    ):
        self._threads = threads
        self.__lists = lists
        self._function = Function
        self.Caller = "MULTITHREADING"
        self.Title = "TOTAL JOB PROGRESS"
        self.Verbose = 3
        self._dct = {}

        self.AlertOnEmptyList()
        if chnk_size != None:
            _quant = int(len(lists) / chnk_size) + 1
        else:
            _quant = self._threads

        _quant = int(512 / self._threads) if _quant >= 512 else _quant
        cpu_ev = math.ceil(len(lists) / _quant)
        if cpu_ev == 0:
            cpu_ev = 1

        self._chnk = [lists[i : i + cpu_ev] for i in range(0, len(lists), cpu_ev)]
        self._indx = [[i, i + cpu_ev] for i in range(0, len(lists), cpu_ev)]
        self.__lists = {i: None for i in range(len(lists))}

    @property
    def Start(self):
        if len(self.__lists) == 0:
            return self._lists
        self._Progress

        self._exc = {}
        for i in range(self._threads):
            T = TemplateThreading(self._function)
            T.i = i + 1
            T.lock = torch.multiprocessing.Manager().Lock()
            self._exc[T.i] = [None, None, T]

        running = []
        f = list(self._exc)[0]
        while True:
            if self._exc[f][2].started == False and len(self._chnk) > 0:
                T = self._exc[f][2]
                self._exc[f][2] = TemplateThreading(self._function)
                self._exc[f][2].i = T.i
                self._exc[f][2].lock = T.lock
                del T

                recv, send = Pipe(True)
                P = Process(target=self._exc[f][2].Exec, args=(send,))
                self._exc[f][0] = P
                self._exc[f][1] = recv
                P.start()

                v = self._chnk.pop(0)
                self._exc[f][1].send(v)
                self._exc[f][2].started = True
                self._exc[f][2]._i = [self._indx.pop(0), v]
                running = [i for i in self._exc if i != f] + [f]
                it = iter(running)
                continue

            it = iter(running) if running[-1] == f else it
            f = next(it)

            if self._exc[f][1] == None:
                continue
            if not self._exc[f][1].poll():
                continue

            _v = self._exc[f][1].recv()
            _v = (
                _v
                if _v != False
                else [self.RecoveredThread(f), self._exc[f][2].MainThread()][-1]
            )

            indx = self._exc[f][2]._i[0]
            self.__lists.update({indx[0] + t: _v[t] for t in range(len(_v))})

            self._exc[f][1].send(True)
            self._exc[f][1].close()
            self._exc[f][0].join()
            self._exc[f][1] = None
            self._exc[f][0] = None

            self._exc[f][2].started = False
            self._exc[f][2].Purge()
            self._Update

            tmp = [f] if len(self._chnk) > 0 else []
            running = tmp + [r for r in running if r != f]
            if (
                len([i for i in self._exc if self._exc[i][2].started]) == 0
                and len(self._chnk) == 0
            ):
                break
            it = iter(running)
            f = next(it)
        del self._exc
        self._Close
        return self.__lists

    @property
    def _lists(self):
        return (
            self.__lists
            if isinstance(self.__lists, list)
            else list(self.__lists.values())
        )

    @property
    def _Progress(self):
        if self.Verbose == 0:
            return
        self._dct["desc"] = self.Title
        self._dct["position"] = 0
        self._dct["leave"] = False
        self._dct["colour"] = "GREEN"
        self._dct["dynamic_ncols"] = True
        self._dct["total"] = len(self._chnk)
        lock = torch.multiprocessing.Manager().Lock()
        with lock:
            bar = tqdm(**self._dct)

        self._dct["obj"] = (lock, bar)

    @property
    def _Update(self):
        if len(self._dct) == 0:
            return
        lock, bar = self._dct["obj"]
        with lock:
            bar.update(1)

    @property
    def _Close(self):
        if len(self._dct) == 0:
            return
        lock, bar = self._dct["obj"]
        with lock:
            bar.close()
