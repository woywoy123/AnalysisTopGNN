
# =========== TRUTH ========= #
def PDGID(a):
    return a.pdgid

def TopsMerged(a):
    ta = [i.index for i in a.Children] 
    if a.Type == "el" or a.Type == "mu":
        ta.append(a.index)
    ta = [j for i in ta for j in i if i != -1]
    if len(set(ta)) > 1:
        return 1
    return 0

def FromTop(a):
    ta = [i.index for i in a.Children] 
    if a.Type == "el" or a.Type == "mu":
        ta.append(a.index)
    ta = [j for i in ta for j in i if i != -1]
    if len(set(ta)) > 0:
        return 1
    return 0

