def res_edge(a, b):
    try: p1 = sum([j.Parent for j in a.Parton], [])
    except AttributeError: p1 = [a]

    try: p2 = sum([j.Parent for j in b.Parton], [])
    except AttributeError: p2 = [b]

    t_1 = list(set(sum([i.Parent for i in p1], [])))
    t_2 = list(set(sum([i.Parent for i in p2], [])))
    t_1 = [1 for t in t_1 if t.FromRes]
    t_2 = [1 for t in t_2 if t.FromRes]
    if len(t_1) and len(t_2): return 1
    return 0

def top_edge(a, b):
    p1, p2 = [], []
    try: p1 += a.Parent
    except AttributeError: pass
    try: p1 += a.Tops
    except AttributeError: pass
    try: p2 += b.Parent
    except AttributeError: pass
    try: p2 += b.Tops
    except AttributeError: pass
    p1, p2 = set(p1), set(p2)
    if not len(p1): return 0
    if not len(p2): return 0
    sc = len([t for t in p1 if t in p2]) > 0
    sc *= len([t for t in p2 if t in p1]) > 0
    return int(sc)


def lep_edge(a, b):
    b_ = (a.is_b + b.is_b) > 0
    l_ = (a.is_lep + b.is_lep) > 0
    return int(b_ and l_)
