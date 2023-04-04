import ROOT as r
import torch
import NuR.Physics.Floats as F
import NuR.Physics.Tensors as T
import NuR.SingleNu.Floats as Sf
import NuR.Sols.Floats as FS
import NuR.Sols.Tensors as TS
import math
import numpy as np
from time import time 

def CompareNumerical(r_ori, r_pyt, string):
    print("(" + string + ") -> Original: ", r_ori, " ||  Pytorch: ", r_pyt, " || Error (%): ", 100*abs(r_pyt - r_ori)/r_ori)

def CompareListNumerical(r_ori, r_pyt, title = "", string = ""):
    print("-> " + title)
    if string == "":
        for i, j in zip(r_ori, r_pyt):
            delta = float(sum(i - j))
            print("ROOT: ", list(i), "PyTorch: ", list(j), " || Error (%): ", 100*abs(delta/sum(abs(i))))
        print("")
        return 
    for i, j, k in zip(r_ori, r_pyt, string):
        CompareNumerical(i, j, k)
    print("")

def RT(c, s, ax):
    R = np.eye(3)*c
    for i in [-1, 0, 1]:
        R[(ax - i)%3, (ax + i)%3] = i*s + (1 - i*i)
    return R

def R(angle, axis):
    '''Rotation matrix about x(0),y(1), or z(2) axis '''
    c, s = math.cos(angle), math.sin(angle)
    R = c * np.eye (3)
    for i in [-1, 0, 1]:
        R[(axis -i)%3, (axis+i)%3] = i*s + (1 - i*i)
    return R

def _H(b_root, mu_root):
    b_xyz = b_root.X(), b_root.Y(), b_root.Z()
    R_z = R(-mu_root.Phi(), 2)
    R_y = R(0.5* math.pi - mu_root.Theta(), 1)
    R_x = next(R(-math.atan2(z,y), 0) for x,y,z in (R_y.dot(R_z.dot(b_xyz )) ,))

    return R_z.T.dot(R_y.T.dot(R_x.T))

def Derivative():
    return R(math.pi / 2, 2).dot(np.diag([1, 1, 0]))

def UnitCircle ():
    return np.diag ([1, 1, -1])

def intersections_ellipse_line (ellipse , line , zero =1e-12):
    _,V = np.linalg.eig(np.cross(line ,ellipse ).T)
    sols = sorted([(v.real / v[2].real, np.dot(line ,v.real )**2 + np.dot(v.real ,ellipse ).dot(v.real )**2) for v in V.T], key=lambda k: k[1])[:2]
    return [s for s, k in sols if k < zero]

def intersections_ellipses (A, B, returnLines =False ):
    LA = np.linalg
    if abs(LA.det(B)) > abs(LA.det(A)):
        A,B = B,A
    e = next(e.real for e in LA.eigvals(LA.inv(A).dot(B)) if not e.imag)
    lines = factor_degenerate (B - e*A)
    points = sum ([ intersections_ellipse_line (A,L) for L in lines ] ,[])
    return (points ,lines) if returnLines else points

def cofactor(A, i, j):
    '''Cofactor[i,j] of 3x3 matrix A'''
    a = A[not i:2 if i==2 else None :2 if i==1 else 1,not j:2 if j==2 else None :2 if j==1 else 1]
    return ( -1)**(i+j) * (a[0 ,0]*a[1 ,1] - a[1 ,0]*a[0 ,1])

def multisqrt (y):
    '''Valid real solutions to y=x*x'''
    return ([] if y < 0 else [0] if y == 0 else (lambda r: [-r, r])( math.sqrt(y)))

def factor_degenerate (G, zero =0):
    if G[0 ,0] == 0 == G[1 ,1]:
        return [[G[0,1], 0, G[1 ,2]] , [0, G[0,1], G[0 ,2] - G[1 ,2]]]
    
    swapXY = abs(G[0 ,0]) > abs(G[1 ,1])
    Q = G[(1 ,0 ,2) ,][: ,(1 ,0 ,2)] if swapXY else G
    Q /= Q[1 ,1]
    q22 = cofactor(Q, 2 ,2)
    if -q22 <= zero:
        lines = [[Q[0,1], Q[1,1], Q[1 ,2]+s] for s in multisqrt (-cofactor(Q, 0, 0))]
    else:
        x0 , y0 = [cofactor(Q, i ,2) / q22 for i in [0, 1]]
        lines = [[m, Q[1,1], -Q[1 ,1]* y0 - m*x0] for m in [Q[0 ,1] + s for s in multisqrt (-q22 )]]
    return [[L[swapXY],L[not swapXY],L[2]] for L in lines]


def SingleNeutrino(b, muon, mT, mW, mN, metX, metY, sigma2):
    sols, b, mu = __initFunction(b, muon, mT, mW, mN) 
    
    S2 = np.vstack ([np.vstack ([np.linalg.inv(sigma2), [0, 0]]).T, [0, 0, 0]])
    V0 = np.outer ([metX , metY , 0], [0, 0, 1])
   
    x1 , y1 , p = sols["x"] , sols["y"] , mu.P()
    Z, w, Om = sols["Z"], sols["w"], math.sqrt(sols["Omega2"])
    x = [[ Z/Om , 0, x1 -p], [w*Z/Om , 0, y1], [ 0, Z, 0]]
    H_til = np.array(x)
    
    R_ = _H(b, mu)
    R_ = R_.dot(H_til)
 
    deltaNu = V0 - R_ 
    X = np.dot(deltaNu.T, S2).dot(deltaNu)
    M = next(XD + XD.T for XD in (X.dot( Derivative ()) ,))
    sols = intersections_ellipses (M, UnitCircle ())
    def calcX2(t):
        return np.dot(t, X).dot(t)
    return [[calcX2(t), R_.dot(t)] for t in sols]

def __initFunction(_b, muon, mT, mW, mN):
    b = r.TLorentzVector()
    b.SetPtEtaPhiE(_b.pt, _b.eta, _b.phi, _b.e)
    
    mu = r.TLorentzVector()
    mu.SetPtEtaPhiE(muon.pt, muon.eta, muon.phi, muon.e)

    c = r.Math.VectorUtil.CosTheta(b,mu)
    s = math.sqrt(1 - c**2)
    
    x0p = - (mT**2 - mW**2 - b.M2())/(2*b.E())
    x0 = - (mW**2 - mu.M2() - mN**2)/(2* mu.E())
    Bb , Bm = b.Beta(), mu.Beta()

    Sx = (x0 * Bm - mu.P()*(1 - Bm **2)) / Bm **2
    Sy = (x0p / Bb - c * Sx) / s

    eps2 = (mW**2 - mN**2) * (1 - Bm**2)

    w = (Bm / Bb - c) / s
    w_ = (-Bm / Bb - c) / s

    Om2 = w**2 + 1 - Bm **2

    x1 = Sx - (Sx + w * Sy)/Om2
    y1 = Sy - (Sx + w * Sy) * w/Om2
    
    Z2 = x1**2 * Om2 - (Sy - w * Sx)**2 - (mW**2 - x0**2 - eps2)
    Z = math.sqrt(max(0, Z2))

    k = [c, s, x0, x0p, Sx, Sy, w, w_, x1, y1, Z, Om2, eps2]
    keys = ["cos", "sin", "x0", "x0p", "Sx", "Sy", "w", "w-", "x", "y", "Z", "Omega2", "eps2"]
    
    return { keys[i] : k[i] for i in range(len(keys)) }, b, mu
        
def _MakeS2V0(event, Sxx, Sxy, Syx, Syy):
    S2 = np.vstack ([np.vstack ([np.linalg.inv([[Sxx, Sxy], [Syx, Syy]]), [0, 0]]).T, [0, 0, 0]])
    metX = F.ToPx(event.met, event.met_phi, "cpu").tolist()[0][0]
    metY = F.ToPy(event.met, event.met_phi, "cpu").tolist()[0][0]
    V0 = np.outer ([metX, metY , 0], [0, 0, 1])
    return S2, V0     

def _MakeH(b, muon, mT, mW, mN):
    sols, b_root, mu_root = __initFunction(b, muon, mT, mW, mN)
    x1 , y1 , p = sols["x"] , sols["y"] , mu_root.P()
    Z, w, Om = sols["Z"], sols["w"], math.sqrt(sols["Omega2"])
    
    H_til = np.array([[ Z/Om , 0, x1 -p], [w*Z/Om , 0, y1], [ 0, Z, 0]])
    R_ = _H(b_root, mu_root)
    R_ = R_.dot(H_til)
    return R_

def _MakeTensor(val, number, device = "cpu", dtp = torch.double):
    return torch.tensor([val for i in range(number)], device = device, dtype = dtp)

def TestFourVector(part):
    p_ = r.TLorentzVector()
    p_.SetPtEtaPhiE(part.pt, part.eta, part.phi, part.e)
    
    p_PyT_f = F.ToPxPyPzE(part.pt, part.eta, part.phi, part.e, "cuda").tolist()[0]
    CompareNumerical(p_.Px(), p_PyT_f[0], "Px")
    CompareNumerical(p_.Py(), p_PyT_f[1], "Py")
    CompareNumerical(p_.Pz(), p_PyT_f[2], "Pz")
    CompareNumerical(p_.E(), p_PyT_f[3], "E")

def TestCosTheta(b, muon):
    b_PyT = F.ToPxPyPzE(b.pt, b.eta, b.phi, b.e, "cuda")
    muon_PyT = F.ToPxPyPzE(muon.pt, muon.eta, muon.phi, muon.e, "cuda")

    b_root = r.TLorentzVector()
    b_root.SetPtEtaPhiE(b.pt, b.eta, b.phi, b.e)

    muon_root = r.TLorentzVector()
    muon_root.SetPtEtaPhiE(muon.pt, muon.eta, muon.phi, muon.e)

    cos_root = r.Math.VectorUtil.CosTheta(b_root, muon_root)
    cos_PyT = T.CosThetaCartesian(b_PyT, muon_PyT).tolist()[0][0]
    CompareNumerical(cos_root, cos_PyT, "CosTheta")

    sin_root = math.sqrt(1 - cos_root**2)
    sin_PyT = T.SinThetaCartesian(b_PyT, muon_PyT).tolist()[0][0]
    CompareNumerical(sin_root, sin_PyT, "SinTheta")

def Testx0(mH, mL, mu_or_b):
    b_root = r.TLorentzVector()
    b_root.SetPtEtaPhiE(mu_or_b.pt, mu_or_b.eta, mu_or_b.phi, mu_or_b.e)
    
    x0_root = - (mH**2 - mL**2 - b_root.M2())/(2*b_root.E())
    x0_PyT = FS.x0Polar(mu_or_b.pt, mu_or_b.eta, mu_or_b.phi, mu_or_b.e, mH, mL, "cuda").tolist()[0][0]
    CompareNumerical(x0_root, x0_PyT, "x0")

def TestBeta(p):
    part_PyT = F.BetaPolar(p.pt, p.eta, p.phi, p.e, "cuda").tolist()[0][0]

    part_root = r.TLorentzVector()
    part_root.SetPtEtaPhiE(p.pt, p.eta, p.phi, p.e)
    part_root = part_root.Beta()

    CompareNumerical(part_root, part_PyT, "Beta")

def TestSValues(b, muon, mTop, mW, mNu):
    from statistics import mean
    
    col = []
    b_root = r.TLorentzVector()
    b_root.SetPtEtaPhiE(b.pt, b.eta, b.phi, b.e)

    muon_root = r.TLorentzVector()
    muon_root.SetPtEtaPhiE(muon.pt, muon.eta, muon.phi, muon.e)
    
    its = 10000
    t1 = time()
    for i in range(its):
        c = r.Math.VectorUtil.CosTheta(b_root, muon_root)
        s = math.sqrt(1 - c**2)
        Bb, Bm = b_root.Beta(), muon_root.Beta() 
   
        x0p = - (mTop**2 - mW**2 - b_root.M2())/(2*b_root.E())
        x0 = - (mW**2 - muon_root.M2() - mNu**2)/(2* muon_root.E())

        Sx_root = (x0 * Bm - muon_root.P()*(1 - Bm **2)) / Bm **2
        Sy_root = (x0p / Bb - c * Sx_root) / s

    t2 = time()
    print("Time: (" + str(its) + ") ", t2 - t1)

    _b = T.ToPxPyPzE(torch.tensor([[b.pt, b.eta, b.phi, b.e] for i in range(its)]))
    _mu = T.ToPxPyPzE(torch.tensor([[muon.pt, muon.eta, muon.phi, muon.e] for i in range(its)]))

    _mW = torch.tensor([[mW] for i in range(its)])
    _mTop = torch.tensor([[mTop] for i in range(its)])
    _mNu = torch.tensor([[mNu] for i in range(its)])
    
    t1 = time()
    x = TS.SxSyCartesian(_b, _mu, _mTop, _mW, _mNu)
    t2 = time()
    print("Time: (" + str(its) +") ", t2 - t1)

    t1 = time()
    Sx_PyT = FS.SxPolar(b.pt, b.eta, b.phi, b.e, muon.pt, muon.eta, muon.phi, muon.e, mW, mNu, "cpu")
    Sy_PyT = FS.SyPolar(b.pt, b.eta, b.phi, b.e, muon.pt, muon.eta, muon.phi, muon.e, mTop, mW, mNu, "cpu")
    CompareNumerical(Sx_root, Sx_PyT.tolist()[0][0], "Sx")
    CompareNumerical(Sy_root, Sy_PyT.tolist()[0][0], "Sy")

def TestIntermediateValues(b, muon, mT, mW, mN):
    b_root = r.TLorentzVector()
    b_root.SetPtEtaPhiE(b.pt, b.eta, b.phi, b.e)

    mu_root = r.TLorentzVector()
    mu_root.SetPtEtaPhiE(muon.pt, muon.eta, muon.phi, muon.e)

    CompareNumerical(b_root.Px(), F.ToPx(b.pt, b.phi, "cpu").tolist()[0][0], "Px")
    CompareNumerical(b_root.Py(), F.ToPy(b.pt, b.phi, "cpu").tolist()[0][0], "Py")
    CompareNumerical(b_root.Pz(), F.ToPz(b.pt, b.eta, "cpu").tolist()[0][0], "Pz")
    
    CompareNumerical(b_root.P(), F.PPolar(b.pt, b.eta, b.phi, "cpu").tolist()[0][0], "P")

def TestEps_W_Omega(b, muon, mW, mN):
    b_root = r.TLorentzVector()
    b_root.SetPtEtaPhiE(b.pt, b.eta, b.phi, b.e)

    muon_root = r.TLorentzVector()
    muon_root.SetPtEtaPhiE(muon.pt, muon.eta, muon.phi, muon.e)
    
    CosTheta = r.Math.VectorUtil.CosTheta(b_root, muon_root)
    SinTheta = math.sqrt(1 - CosTheta**2)

    eps2_root = ( mW**2 - mN**2 )*( 1 - muon_root.Beta()**2 )
    eps2_PyT = FS.Eps2Polar(muon.pt, muon.eta, muon.phi, muon.e, mW, mN, "cpu").tolist()[0][0]
    CompareNumerical(eps2_root, eps2_PyT, "eps2")

    w = ( ( muon_root.Beta()/b_root.Beta() ) - CosTheta ) / SinTheta
    w_PyT = FS.wPolar(b.pt, b.eta, b.phi, b.e, muon.pt, muon.eta, muon.phi, muon.e, 1, "cpu").tolist()[0][0]
    CompareNumerical(w, w_PyT, "w")

    w_ = ( - ( muon_root.Beta()/b_root.Beta() ) - CosTheta ) / SinTheta
    w__PyT = FS.wPolar(b.pt, b.eta, b.phi, b.e, muon.pt, muon.eta, muon.phi, muon.e, -1, "cpu").tolist()[0][0]
    CompareNumerical(w_, w__PyT, "w_")

    Om2 = w**2 + 1 - muon_root.Beta()**2 
    Om2_PyT = FS.Omega2Polar(b.pt, b.eta, b.phi, b.e, muon.pt, muon.eta, muon.phi, muon.e, "cpu").tolist()[0][0]
    CompareNumerical(Om2, Om2_PyT, "Omega2")

def TestxyZ2(b, muon, mT, mW, mN):
    its = 1
    t1 = time() 
    b_root = r.TLorentzVector()
    b_root.SetPtEtaPhiE(b.pt, b.eta, b.phi, b.e)

    mu_root = r.TLorentzVector()
    mu_root.SetPtEtaPhiE(muon.pt, muon.eta, muon.phi, muon.e)
    for i in range(its): 
        c_root = r.Math.VectorUtil.CosTheta(b_root, mu_root)
        s_root = math.sqrt(1 - c_root**2)
   
        x0p = - (mT**2 - mW**2 - b_root.M2())/(2*b_root.E())
        x0 = - (mW**2 - mu_root.M2() - mN**2)/(2* mu_root.E())
        Bb , Bm = b_root.Beta(), mu_root.Beta()

        Sx_root = (x0 * Bm - mu_root.P()*(1 - Bm **2)) / Bm **2
        Sy_root = (x0p / Bb - c_root * Sx_root) / s_root

        eps2 = (mW**2 - mN**2) * (1 - Bm**2)

        w = (Bm / Bb - c_root) / s_root
        w_ = (-Bm / Bb - c_root) / s_root

        Om2 = w**2 + 1 - Bm **2

        x1 = Sx_root - (Sx_root + w * Sy_root)/Om2
        y1 = Sy_root - (Sx_root + w * Sy_root) * w/Om2
        
        Z = x1**2 * Om2 - (Sy_root - w * Sx_root)**2 - (mW**2 - x0**2 - eps2)
    t2 = time() 
    print("Original time: (" + str(its) + ")", t2-t1)

    _b  = torch.tensor([[b.pt, b.eta, b.phi, b.e] for i in range(its)], device = "cpu")
    _mu = torch.tensor([[muon.pt, muon.eta, muon.phi, muon.e] for i in range(its)], device = "cpu")
    _mT = torch.tensor([[mT] for i in range(its)], device = "cpu")
    _mW = torch.tensor([[mW] for i in range(its)], device = "cpu")
    _mN = torch.tensor([[mN] for i in range(its)], device = "cpu")
    
    t1 = time()
    t = TS.AnalyticalSolutionsPolar(_b, _mu, _mT, _mW, _mN)
    t2 = time()
    print("C++ time: (" + str(its) + ")", t2-t1)

    k = [c_root, s_root, x0, x0p, Sx_root, Sy_root, w, w_, x1, y1, max(0, math.sqrt(Z)), Om2, eps2]
    keys = ["cos", "sin", "x0", "x0p", "Sx", "Sy", "w", "w-", "x", "y", "Z", "Omega2", "eps2"]

    d = FS.AnalyticalSolutionsPolar(b.pt, b.eta, b.phi, b.e, muon.pt, muon.eta, muon.phi, muon.e, mT, mW, mN, "cpu").tolist()[0]; 
    d = { keys[i] : [ d[i], k[i] ] for i in range(len(keys)) }
    
    for i in d:
        CompareNumerical(d[i][1], d[i][0], i)

def TestS2V0(sxx, sxy, syx, syy, met, phi):
    import numpy as np
    import torch.nn.functional as G
    
    sigma2 = [[sxx, sxy], [syx, syy]]
    sigma2 = np.linalg.inv(sigma2)
    sigma2 = np.vstack([sigma2, [0, 0]])
    sigma2 = sigma2.T
    sigma2 = np.vstack([sigma2, [0, 0, 0]])
    print(sigma2)
    
    print("--------")
    n = 5
    matrix = Sf.Sigma2_F(sxx, sxy, syx, syy, "cuda")
    sxx_ = torch.tensor([sxx for i in range(n) ], dtype = np.float, device = "cuda").view(-1, 1)
    syx_ = torch.tensor([syx for i in range(n) ], dtype = np.float, device = "cuda").view(-1, 1)
    sxy_ = torch.tensor([sxy for i in range(n) ], dtype = np.float, device = "cuda").view(-1, 1)
    syy_ = torch.tensor([syy for i in range(n) ], dtype = np.float, device = "cuda").view(-1, 1)
    matrix_ = Sf.Sigma2_T(sxx_, sxy_, syx_, syy_)
    print(matrix_)
    print("--------") 

    metx = F.ToPx(met, phi, "cuda")
    metx = torch.cat([metx for i in range(n)], dim = 0)
    mety = F.ToPy(met, phi, "cuda")
    mety = torch.cat([mety for i in range(n)], dim = 0)   
    _tmp = torch.cat([torch.tensor([[0.]], device = "cuda") for i in range(n)], dim = 0)
    _tmp2 = torch.cat([torch.tensor([[1.]], device = "cuda") for i in range(n)], dim = 0)
    _tmp2 = torch.cat([_tmp, _tmp, _tmp2], dim = -1).view(-1, 1, 3)
    _tmp = torch.cat([metx, mety, _tmp], dim = -1)

    V0 = np.outer([metx.tolist()[0][0] , mety.tolist()[0][0] , 0], [0, 0, 1])
    print(V0)
    
    V0_ = Sf.V0_T(metx, mety)
    print(V0_)

def TestR_T(b, muon, mT, mW, mN):
    n = 10000

    _b = torch.tensor([[b.pt, b.eta, b.phi] for i in range(n)], device = "cuda")
    _mu = torch.tensor([[muon.pt, muon.eta, muon.phi] for i in range(n)], device = "cuda")
    _a = torch.tensor([muon.phi for i in range(n)], device = "cuda")

    sols, b_root, mu_root = __initFunction(b, muon, mT, mW, mN)
    x_r = b_root.X(), b_root.Y(), b_root.Z()
    x = F.ToPxPyPz(b.pt, b.eta, b.phi, "cuda").tolist()[0]
    CompareListNumerical(x_r, x, "ROOT X(), Y(), Z() for b-quark", ["X", "Y", "Z"]) 

    x_r = mu_root.X(), mu_root.Y(), mu_root.Z()
    x = F.ToPxPyPz(muon.pt, muon.eta, muon.phi, "cuda").tolist()[0]
    CompareListNumerical(x_r, x, "ROOT X(), Y(), Z() for muon", ["X", "Y", "Z"]) 
   
    theta_r = mu_root.Theta()
    theta_PyT = F.ThetaPolar(muon.pt, muon.eta, muon.phi, "cuda").tolist()[0][0]
    CompareNumerical(theta_r, theta_PyT, "Theta")
    print("") 

    # ======= Checking the Rotation ====== #
    c_r_mu, s_r_mu = math.cos(-mu_root.Phi()), math.sin(mu_root.Phi())
    
    Rx_r = RT(c_r_mu, s_r_mu, 0)
    Rx_PyT = T.Rx(_a).tolist()[0]
    CompareListNumerical(Rx_r, Rx_PyT, "Rx Rotation")
 
    Ry_r = RT(c_r_mu, s_r_mu, 1)
    Ry_PyT = T.Ry(_a).tolist()[0]
    CompareListNumerical(Ry_r, Ry_PyT, "Ry Rotation")
 
    Rz_r = RT(c_r_mu, s_r_mu, 2)
    Rz_PyT = T.Rz(_a).tolist()[0]
    CompareListNumerical(Rz_r, Rz_PyT, "Rz Rotation")
   
    # ======== Checking Algorihtm ======= #
    R_z = R(-mu_root.Phi(), 2)
    R_zPyT = F.Rz(-muon.phi, "cpu").tolist()[0]
    CompareListNumerical(R_z, R_zPyT, "Rz Muon")
   
    R_y = R(0.5* math.pi - mu_root.Theta(), 1)
    R_yPyT = F.Ry(0.5 * math.pi - F.ThetaPolar(muon.pt, muon.eta, muon.phi, "cpu").tolist()[0][0], "cpu").tolist()[0]
    CompareListNumerical(R_y, R_yPyT, "Ry Muon")

    b_xyz = b_root.X(), b_root.Y(), b_root.Z()
    R_x = next(R(-math.atan2(z,y), 0) for x,y,z in (R_y.dot(R_z.dot(b_xyz )) ,))

    Ro_PyT = Sf.R_T(_b, _mu)
    Res = R_z.T.dot(R_y.T.dot(R_x.T))
    CompareListNumerical(Res, Ro_PyT.tolist()[0], "Rotation Algo")

    t1 = time()
    for i in range(n):
        R_z = R(-mu_root.Phi(), 2)
        R_y = R(0.5* math.pi - mu_root.Theta(), 1)
        R_x = next(R(-math.atan2(z,y), 0) for x,y,z in (R_y.dot(R_z.dot(b_xyz )) ,))
        Res = R_z.T.dot(R_y.T.dot(R_x.T))
    t2 = time() 
    print("Original time: (" + str(n) + ")", t2-t1)
    
    t1 = time()
    Ro_PyT = Sf.R_T(_b, _mu)
    t2 = time() 
    print("C++ time: (" + str(n) + ")", t2-t1)

def TestH(b, muon, mT, mW, mN):

    n = 5
    device = "cpu"
    _b = torch.tensor([[b.pt, b.eta, b.phi, b.e] for i in range(n)], device = device, dtype = torch.double).view(-1, 4)
    _mu = torch.tensor([[muon.pt, muon.eta, muon.phi, muon.e] for i in range(n)], device = device, dtype = torch.double).view(-1, 4)
    _mT = torch.tensor([[mT] for i in range(n)], device = device, dtype = torch.double).view(-1, 1)
    _mW = torch.tensor([[mW] for i in range(n)], device = device, dtype = torch.double).view(-1, 1)
    _mN = torch.tensor([[mN] for i in range(n)], device = device, dtype = torch.double).view(-1, 1)

    sols, b_root, mu_root = __initFunction(b, muon, mT, mW, mN)
   
    x1 , y1 , p = sols["x"] , sols["y"] , mu_root.P()
    Z, w, Om = sols["Z"], sols["w"], math.sqrt(sols["Omega2"])
    x = [[ Z/Om , 0, x1 -p], [w*Z/Om , 0, y1], [ 0, Z, 0]]
    H_til = np.array(x)

    R_ = _H(b_root, mu_root)
    R_ = R_.dot(H_til)
    
    Z_PyT = Sf.H_T(_b, _mu, _mT, _mW, _mN)
    CompareListNumerical(R_, Z_PyT.tolist()[0], "H value")

def TestInit(event, Sxx, Sxy, Syx, Syy, b, muon, mT, mW, mN):

    n = 2
    device = "cuda"
    _b  = _MakeTensor([b.pt, b.eta, b.phi, b.e], n, device)
    _mu = _MakeTensor([muon.pt, muon.eta, muon.phi, muon.e], n, device)
    _mT = _MakeTensor([mT], n, device)
    _mW = _MakeTensor([mW], n, device)
    _mN = _MakeTensor([mN], n, device)
    _met = _MakeTensor([event.met], n, device)
    _phi = _MakeTensor([event.met_phi], n, device)
    _Sxx = _MakeTensor([Sxx ], n, device)
    _Sxy = _MakeTensor([Sxy ], n, device) 
    _Syx = _MakeTensor([Syx ], n, device) 
    _Syy = _MakeTensor([Syy ], n, device)

    x = F.ToPx(event.met, event.met_phi, "cpu").tolist()[0][0]
    y = F.ToPy(event.met, event.met_phi, "cpu").tolist()[0][0]
    # ===== M calc ===== 
    
    print("Device: ", device)
    t1 = time()
    for i in range(n):
        r_sol = SingleNeutrino(b, muon, mT, mW, mN, x, y, [[Sxx, Sxy], [Syx, Syy]])
    t2 = time()
    print("Python (" + str(n) + "): ", t2 - t1)
    
    t1c = time()
    _sol = Sf.SolT(_b, _mu, _mT, _mW, _mN, _met, _phi, _Sxx, _Sxy, _Syx, _Syy)
    t2c = time()
    
    print("C++ (" + str(n) + "): ", t2c - t1c)
    for i in range(2):
        for j in range(3):
            CompareNumerical(r_sol[i][1].tolist()[j], _sol[0][0].tolist()[1-i][j], "Neutrino Solutions")
        CompareNumerical(r_sol[i][0], _sol[1].tolist()[0][1-i][0], "Chi2")
    print("Improvement (x): ", (t2 - t1)/(t2c - t1c))

