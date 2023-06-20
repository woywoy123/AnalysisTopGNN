def res_edge(a, b):
    p1, p2 = [], []
    try:
        p1 += a.Parent
    except:
        pass

    try:
        p1 += a.Tops
    except:
        pass

    try:
        p2 += b.Parent
    except:
        pass

    try:
        p2 += b.Tops
    except:
        pass

    p1, p2 = [p for p in set(p1) if p.FromRes == 1], [
        p for p in set(p2) if p.FromRes == 1
    ]
    return len(p1) > 0 and len(p2) > 0


def top_edge(a, b):
    p1, p2 = [], []
    try:
        p1 += a.Parent
    except:
        pass

    try:
        p1 += a.Tops
    except:
        pass

    try:
        p2 += b.Parent
    except:
        pass

    try:
        p2 += b.Tops
    except:
        pass
    p1, p2 = set(p1), set(p2)
    if len(p1) == 0:
        return False
    if len(p2) == 0:
        return False
    sc = len([t for t in p1 if t in p2]) > 0
    sc *= len([t for t in p2 if t in p1]) > 0
    return sc


def lep_edge(a, b):
    b_ = (a.is_b + b.is_b) > 0
    l_ = (a.is_lep + b.is_lep) > 0

    return b_ and l_
