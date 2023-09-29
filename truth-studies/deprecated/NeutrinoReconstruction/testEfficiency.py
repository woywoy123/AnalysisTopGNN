def getIndex(string):
    return string.split("_")[-1]

def passOrFail(dict):
    doesPass = False
    bPartons = {tj: [p for p in dict[tj] if "b" in p] for tj in dict}
    print(f"bPartons = {bPartons}")
    for tj, b in bPartons.items():
        print(f"(tj, b) = ({tj}, {b})")
        if not b: 
            print("No b, continuing")
            continue
        for bp in b:
            print(f"bp = {bp}")
            matches = 0
            for tj2 in dict:
                print(f"tj2 = {tj2}")
                if tj == tj2: 
                    print(f"tj = tj2, continuing")
                    continue
                print(f"Index of bp = {getIndex(bp)}")
                print(f"Indices of quarks in tj2 = {[getIndex(p) for p in dict[tj2] if p != 'g' and 'b' not in p]}")
                if getIndex(bp) in [getIndex(p) for p in dict[tj2] if p != "g" and "b" not in p]:
                    print(f"Adding 1 to matches")
                    matches += 1
            if matches >=2 :
                print("Pass!")
                doesPass = True
    return doesPass

def passOrFail2(dict):
    doesPass = False
    allPartonsIndex = {i: [getIndex(p) for p in tj] for i,tj in enumerate(dict.values())}
    print(f"allPartonsIndex = {allPartonsIndex}")
    print(f"Intersection = {set.intersection(*map(set,allPartonsIndex.values()))}")
    if set.intersection(*map(set,allPartonsIndex.values())):
        doesPass = True 
    print(f"Returning {doesPass}")
    return doesPass


case1 = {"tj0": ["b_4","g_1","g_1"], "tj1": ["d_4","g_4","g_4"], "tj2": ["u_4","g_2"]}
case2 = {"tj0": ["b_4"], "tj1": ["u_4"], "tj2": ["g_1"]}
case3 = {"tj0": ["b_3"], "tj1": ["d_3"], "tj2": ["u_3","g_4"]}
case4 = {"tj0": ["b_1","u_4"], "tj1": ["u_4"], "tj2": ["d_4"]}
case5 = {"tj0": ["b_1","u_4"], "tj1": ["u_1"], "tj2": ["d_1","u_2"]}
case6 = {"tj0": ["b_1"], "tj1": ["d_3"], "tj2": ["b_3","u_3"]}
case7 = {"tj0": ["b_1"], "tj1": ["d_1"], "tj2": ["b_4","u_1"]}
case8 = {"tj0": ["b_1","b_4"], "tj1": ["u_1"], "tj2": ["d_1"]}
case9 = {"tj0": ["b_1","b_3"], "tj1": ["u_1"], "tj2": ["d_3"]}
case10 = {"tj0": ["b_1"], "tj1": ["u_1"], "tj2": ["g_1"]}

print(f"=> Case 1: {passOrFail2(case1)}")
print(f"=> Case 2: {passOrFail2(case2)}")
print(f"=> Case 3: {passOrFail2(case3)}")
print(f"=> Case 4: {passOrFail2(case4)}")
print(f"=> Case 5: {passOrFail2(case5)}")
print(f"=> Case 6: {passOrFail2(case6)}")
print(f"=> Case 7: {passOrFail2(case7)}")
print(f"=> Case 8: {passOrFail2(case8)}")
print(f"=> Case 9: {passOrFail2(case9)}")
print(f"=> Case 10: {passOrFail2(case10)}")

