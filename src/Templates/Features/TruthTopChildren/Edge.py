def res_edge(a, b):
    tops = a.Parent + b.Parent
    return int(sum([i.FromRes for i in tops]) == 2)

def top_edge(a, b):
    try: return a.Parent[0] == b.Parent[0]
    except: return False

def lep_edge(a, b):
    tops = list(set(a.Parent + b.Parent))
    if len(tops) != 1: return False
    is_b = (a.is_b + b.is_b) > 0
    is_lep = (a.is_lep + b.is_lep) > 0
    return is_b and is_lep
