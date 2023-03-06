import torch 
import vector
import numpy as np 

mW = 80.385*1000 # MeV : W Boson Mass
mN = 0           # GeV : Neutrino Mass

def AssertEquivalence(truth, pred, threshold = 0.0001):
    diff = abs(truth - pred)
    if truth == 0:
        truth += 1
    diff = abs((diff/truth))*100
    if diff < threshold:
        return True 
    print("-> ", diff, truth, pred)
    return False

def AssertEquivalenceList(truth, pred, threshold = 0.0001):
    for i, j in zip(truth, pred):
        if AssertEquivalence(i, j) == False:
            return False
    return True

def AssertEquivalenceRecursive(truth, pred, threshold = 0.001):
    try:
        return AssertEquivalence(float(truth), float(pred), threshold)
    except:
        for i, j in zip(truth, pred):
            if AssertEquivalenceRecursive(i, j, threshold) == False:
                return False 
        return True 

def AssertSimilarSets(pred1, pred2, threshold):
    if len(pred1) != len(pred2):
        return False
    p1, p2 = [], []
    for i, j in zip(pred1, pred2):
        if sum(i) != 0:
            p1.append(i)
        if sum(j) != 0:
            p2.append(j)
    
    for i in p1:
        diff1 = {}
        for k in p2:
            diff1[sum([abs((l1 -l2)/l1)*100 for l1, l2 in zip(k, i)])**0.5] = [k, i] 
        l = list(diff1)
        l.sort()
        trig = False
        if l[0] > threshold:
            print(l[0], diff1[l[0]])
            trig = True
        if trig:
            return True 
    return False


def AssertSolutionSets(truth, pred1, pred2, threshold):
    
    p1, p2 = [], []
    for k, p in zip(pred1, pred2):
        if sum(k) == 0 and sum(p) == 0:
            continue
        p1.append(k)
        p2.append(p)
    if len(truth) == 0:
        if len(p1) + len(p2) != 0:
            print(p1, p2, truth)

    for i, j in truth:
        diff1 = {}
        diff2 = {}
        for k, p in zip(p1, p2):
            if sum(k) == 0 and sum(p) == 0:
                continue
            diff1[sum([abs((l1 -l2)/l1)*100 for l1, l2 in zip(k, i.tolist())])**0.5] = [k, i.tolist()] 
            diff2[sum([abs((l1 -l2)/l1)*100 for l1, l2 in zip(p, j.tolist())])**0.5] = [p, j.tolist()] 
        
        l = list(diff1)
        l.sort()
        trig = False
        if l[0] > threshold:
            print(diff1[l[0]])
            trig = True

        l = list(diff2)
        l.sort()
        if l[0] > threshold:
            print(diff2[l[0]])
            trig = True
        if trig:
            return True 
    return False



def MakeTensor(inpt, device = "cpu"):
    return torch.tensor([inpt], device = device)

def PerformanceInpt(var, inpt = "(p_x, p_y, p_z)", Coord = "C"):
    strg_TC = "T" + Coord + "." + var + inpt
    strg_CC = "C" + Coord + "." + var + inpt
   
    t1 = time()
    res_c = eval(strg_TC)
    diff1 = time() - t1

    t1 = time()
    res = eval(strg_CC)
    diff2 = time() - t1
    
    print("--- Testing Performance Between C++ and CUDA of " + var + " ---")
    print("Speed Factor (> 1 is better): ", diff1 / diff2)
    AssertEquivalenceRecursive(res_c, res)

class SampleTensor:

    def __init__(self, b, mu, ev, top, device = "cpu", S = [[100, 0], [0, 100]]):
        self.device = device
        self.n = len(b)
        
        self.Sxx = self.MakeTensor(S[0][0])
        self.Sxy = self.MakeTensor(S[0][1])
        self.Syx = self.MakeTensor(S[1][0])
        self.Syy = self.MakeTensor(S[1][1])

        self.b = self.MakeKinematics(0, b)
        self.mu = self.MakeKinematics(0, mu)
        
        self.b_ = self.MakeKinematics(1, b)
        self.mu_ = self.MakeKinematics(1, mu)
       
        self.mT = torch.tensor([[top[i][0].Mass] for i in range(self.n)], device = self.device, dtype = torch.float64)
        self.mW = self.MakeTensor(mW / 1000)
        self.mN = self.MakeTensor(mN / 1000)

        self.MakeEvent(ev)

    def MakeKinematics(self, idx, obj):
        return torch.tensor([[i[idx].pt/1000., i[idx].eta, i[idx].phi, i[idx].e/1000.] for i in obj], device = self.device, dtype = torch.float64)
    
    def MakeEvent(self, obj):
        self.met = torch.tensor([[ev.met / 1000.] for ev in obj], device = self.device, dtype = torch.float64)
        self.phi = torch.tensor([[ev.met_phi] for ev in obj], device = self.device, dtype = torch.float64)

    def MakeTensor(self, val):
        return torch.tensor([[val] for i in range(self.n)], device = self.device, dtype = torch.float64)

    def __iter__(self):
        self.it = -1
        return self
    
    def __next__(self):
        self.it += 1
        if self.it == self.n:
            raise StopIteration()

        return [self.b[self.it], self.mu[self.it], 
                self.b_[self.it], self.mu_[self.it], 
                self.met[self.it], self.phi[self.it], 
                self.mT[self.it], self.mW[self.it], self.mN[self.it]]

class SampleVector:
    def __init__(self, b, mu, ev, top):

        self.n = len(ev)
        self.b = [self.MakeKinematics(0, i) for i in b]
        self.b_ = [self.MakeKinematics(1, i) for i in b]       

        self.mu = [self.MakeKinematics(0, i) for i in mu]
        self.mu_ = [self.MakeKinematics(1, i) for i in mu]       

        self.met_x = []
        self.met_y = []
        
        for i in ev:
            x, y = self.MakeEvent(i)
            self.met_x.append(x)
            self.met_y.append(y)

        self.mT = [top[i][0].Mass for i in range(self.n)] 
        self.mW = [mW/1000 for i in range(self.n)]
        self.mN = [mN/1000 for i in range(self.n)]

    def MakeKinematics(self, idx, obj):
        r = vector.obj(pt=obj[idx].pt/1000., eta=obj[idx].eta, phi=obj[idx].phi, E=obj[idx].e/1000.)
        return r

    def MakeEvent(self, obj):
        x = (obj.met / 1000.) * np.cos(obj.met_phi)
        y = (obj.met / 1000.) * np.sin(obj.met_phi)
        return x, y

    def __iter__(self):
        self.it = -1
        return self
    
    def __next__(self):
        self.it += 1
        if self.it == self.n:
            raise StopIteration()

        return [self.b[self.it], self.mu[self.it], 
                self.b_[self.it], self.mu_[self.it], 
                self.met_x[self.it], self.met_y[self.it], 
                self.mT[self.it], self.mW[self.it], self.mN[self.it]]
