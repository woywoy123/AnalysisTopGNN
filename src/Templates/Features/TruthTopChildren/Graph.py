def signal(ev):
    try:
        return len([i for i in ev.Tops if i.FromRes == 1]) == 2
    except:
        False


def ntops(ev):
    try:
        t = len(ev.Tops)
    except:
        return 0
    return t - 1 if t > 4 else t


def n_nu(ev):
    try:
        return sum([c.is_nu for c in ev.TopChildren])
    except:
        return 0


def n_jets(ev):
    return len([c for c in ev.TopChildren if not c.is_nu or not c.is_lep])


def n_lep(ev):
    return len([k for k in ev.TopChildren if k.is_lep])


def met(ev):
    return ev.met


def phi(ev):
    return ev.met_phi
