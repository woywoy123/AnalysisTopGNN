def res_node(a):
    try:
        return sum([i.FromRes for i in a.Parent]) > 0
    except:
        return False


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
