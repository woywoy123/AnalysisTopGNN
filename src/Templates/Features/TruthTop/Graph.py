def signal(ev):
    try:
        return len([i for i in ev.Tops if i.FromRes == 1]) == 2
    except:
        0


def ntops(ev):
    try:
        t = len(ev.Tops)
    except:
        return 0
    return t - 1 if t > 4 else t


def met(ev):
    return ev.met


def phi(ev):
    return ev.met_phi
