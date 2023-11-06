def res_edge(a, b):
    p1, p2 = [], []
    try: p1 += a.Tops
    except AttributeError: p1 += a.Parent

    try: p2 += b.Tops
    except AttributeError: p2 += b.Parent

    p1 = set([i for i in p1 if i.FromRes])
    p2 = set([i for i in p2 if i.FromRes])
    if not len(p1): return 0
    if not len(p2): return 0
    return 1

def top_edge(a, b):
    p1, p2 = [], []
    try: p1 += a.Tops
    except AttributeError: p1 += a.Parent
    try: p2 += b.Tops
    except AttributeError: p2 += b.Parent

    p1, p2 = set(p1), set(p2)
    if not len(p1): return 0
    if not len(p2): return 0
    sc = len([t for t in p1 if t in p2]) > 0
    sc *= len([t for t in p2 if t in p1]) > 0
    return int(sc)


def lep_edge(a, b):
    b_ = (a.is_b + b.is_b) > 0
    l_ = (a.is_lep + b.is_lep) > 0

    return b_ and l_
