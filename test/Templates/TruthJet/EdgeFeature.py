



# ============= Truth =================== #
def Index(a, b):
    ta = [i.index for i in a.Children]
    tb = [i.index for i in b.Children]
    
    if a.Type == "el" or a.Type == "mu":
        ta.append(a.index)
    if b.Type == "el" or b.Type == "mu":
        tb.append(b.index)

    if len(ta) == 0:
        return 0
    if len(tb) == 0:
        return 0
    
    x = [p for p in ta for j in tb if p == j]
    if len(x) > 0:
        return  1
    else:
        return 0


