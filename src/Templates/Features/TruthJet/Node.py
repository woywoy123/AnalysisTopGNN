def one_top(a):
    p = []
    try:
        p += a.Parent
    except:
        pass
    try:
        p += a.Tops
    except:
        pass
    p_ = set(p)
    return len([t for t in p_ if t.Type == "top"]) == 1


def top_node(a):
    p = []
    try:
        p += a.Parent
    except:
        pass
    try:
        p += a.Tops
    except:
        pass
    p_ = set(p)
    return len([t for t in p_ if t.Type == "top"]) > 0


def res_node(a):
    p = []
    try:
        p += a.Parent
    except:
        pass
    try:
        p += a.Tops
    except:
        pass
    p_ = set(p)
    return len([t for t in p_ if t.Type == "top" and t.FromRes == 1]) > 0


def eta(a):
    return a.eta


def energy(a):
    return a.e


def pT(a):
    return a.pt


def phi(a):
    return a.phi


def is_lep(a):
    return a.is_lep


def is_b(a):
    return a.is_b


def is_nu(a):
    return a.is_nu
