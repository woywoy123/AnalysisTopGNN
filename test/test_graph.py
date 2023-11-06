from random import random
import pyc
import torch

def test_edge_feature_aggregation():
    def aggregation(edge_index, pred, pmu, incl_zero = False):
        cls_ = torch.max(pred)
        output = {}
        p = pmu.size(0)
        for i in torch.arange(cls_+1):
            if i == 0 and not incl_zero: continue
            sel = int(i.item())
            pair_m = torch.ones(p, p, dtype = torch.long)*-1

            e_i, e_j = edge_index
            # Make sure to add the self loops
            pair_m[e_i, e_i] = e_i

            # now remove the self loops (avoid double counting)
            msk_self = e_i != e_j

            # remove the edges based on the prediction 
            msk = (pred.view(-1) == i)*msk_self
            e_i, e_j = edge_index[:, msk.view(-1)]
            pair_m[e_i, e_j] = e_j
            pair_m, _ = pair_m.sort(-1, True)

            # aggregate the incoming edges
            pmu_i = torch.zeros_like(pmu)
            for this, j in zip(range(p), pair_m): pmu_i[this] += pmu[j[j > -1], :].sum(0)

            # find the unique node aggregation
            clusters, revert = pair_m.unique(dim = 0, return_inverse = True)
            pmu_u = torch.zeros(len(clusters), pmu.size(1))
            for this, j in zip(range(len(clusters)), clusters):
                get = j[j > -1]
                pmu_u[this] += pmu[get, :].sum(0)

            output[int(i)] = {}
            output[int(i)]["clusters"] = clusters
            output[int(i)]["unique_sum"] = pmu_u
            output[int(i)]["reverse_clusters"] = revert
            output[int(i)]["node_sum"] = pmu_i
        return output

    def compare(truth, pred):
        for i in truth:
            res_t = truth[i]
            res_c = pred[i]
            for k in res_t:
                val_t = res_t[k].to(device = "cpu")
                val_c = res_c[k].to(device = "cpu")
                attest = abs(val_t - val_c) > 0
                assert attest.sum(-1).sum(-1) == 0

    # create a node feature of length 10
    n = 4
    n_nodes = 10
    nodes = torch.tensor([[int(1 + 10*random()*(t+1)) for _ in range(n)] for t in range(n_nodes)])

    # create some fake truth connections 
    n_cls = 3 # classifications
    p_ = 0.4 # probability that nodes are always connected with the same class, i.e. more equal clusters
    edges_t = torch.tensor([[(random() > p_)*int(random()*n_cls)] for _ in range(n_nodes**2)])

    # create the edge index
    edge_i = torch.tensor([t for t in range(n_nodes) for _ in range(n_nodes)])
    edge_j = torch.tensor([t for _ in range(n_nodes) for t in range(n_nodes)])
    edge_index = torch.cat([edge_i.view(1, -1), edge_j.view(1, -1)], dim = 0)

    # manually compute the truth clusters
    dic = {cls : {n : nodes[n].clone() for n in range(n_nodes)} for cls in range(n_cls)}
    for i, src, dst in zip(edges_t, edge_i, edge_j):
        if src == dst: continue
        dic[i.item()][src.item()] += nodes[dst]

    res = {}
    for cls in dic:
        res[cls] = []
        for node in dic[cls]: res[cls].append(dic[cls][node].view(1, -1))
        res[cls] = torch.cat(res[cls], dim = 0)

    out = aggregation(edge_index, edges_t, nodes, True)
    for i in out:
        nodes_ = res[i]
        attest = nodes_ != out[i]["node_sum"]
        assert attest.sum(-1).sum(-1) == 0


    x = pyc.Graph.Base.edge_aggregation(edge_index, edges_t, nodes, True)
    compare(out, x)

    dev = "cuda" if torch.cuda.is_available() else "cpu"
    edge_index = edge_index.to(device = dev)
    edges_t = edges_t.to(device = dev)
    nodes = nodes.to(device = dev)
    cu = pyc.Graph.Base.edge_aggregation(edge_index, edges_t, nodes, True)
    compare(out, cu)

    a, b, c, d = [nodes[:, i] for i in range(4)]
    x = pyc.Graph.Cartesian.edge(edge_index, edges_t, a, b, c, d, True)
    compare(out, x)

    x = pyc.Graph.Cartesian.edge(edge_index, edges_t, nodes, True)
    compare(out, x)

    node_t = edges_t.view(-1, n_nodes)[:, 0]
    a, b, c, d = [nodes[:, i] for i in range(4)]
    x = pyc.Graph.Cartesian.node(edge_index, node_t, a, b, c, d, True)
    x1 = pyc.Graph.Cartesian.node(edge_index, node_t, nodes, True)
    compare(x1, x)

    edge_index = edge_index.to(device = "cpu")
    edges_t = edges_t.to(device = "cpu")
    nodes = nodes.to(device = "cpu")
    a, b, c, d = [nodes[:, i] for i in range(4)]
    x = pyc.Graph.Cartesian.edge(edge_index, edges_t, a, b, c, d, True)
    compare(out, x)

    x = pyc.Graph.Cartesian.edge(edge_index, edges_t, nodes, True)
    compare(out, x)

    node_t = edges_t.view(-1, n_nodes)[:, 0]
    a, b, c, d = [nodes[:, i] for i in range(4)]
    x = pyc.Graph.Cartesian.node(edge_index, node_t, a, b, c, d, True)
    x1 = pyc.Graph.Cartesian.node(edge_index, node_t, nodes, True)
    compare(x1, x)

def test_edge_aggregation_nodupl():

    # create a node feature of length 10
    n_nodes = 100
    dim = 100
    nodes = torch.tensor([[float(random()) for _ in range(dim)] for t in range(n_nodes)])

    # create some fake truth connections 
    n_cls = 2 # classifications
    p_ = 0.4 # probability that nodes are always connected with the same class, i.e. more equal clusters
    edges_t = torch.tensor([[(random() > p_)*int(random()*n_cls)] for _ in range(n_nodes**2)])

    # create the edge index
    edge_i = torch.tensor([t for t in range(n_nodes) for _ in range(n_nodes)])
    edge_j = torch.tensor([t for _ in range(n_nodes) for t in range(n_nodes)])
    edge_index = torch.cat([edge_i.view(1, -1), edge_j.view(1, -1)], dim = 0)

    dev = "cuda" if torch.cuda.is_available() else "cpu"
    edge_index = edge_index.to(device = dev)
    nodes = nodes.to(device = dev)
    edges_t = edges_t.to(device = dev)
    edge_index = torch.cat([edge_index, edge_index], -1)
    edges_t = torch.cat([edges_t, edges_t], 0)

    x = pyc.Graph.Base.edge_aggregation(edge_index, edges_t, nodes.to(dtype = torch.float), True)[1]
    clust, rev = x["clusters"], x["reverse_clusters"]
    clust = clust[rev]
    clust_l, node_l = clust.tolist(), nodes.tolist()
    non_dupl = []
    x = 0
    for i in clust_l:
        non_dupl.append([sum([node_l[k][f] for k in set(i) if k != -1]) for f in range(dim)])

    try: x = pyc.Graph.Base.unique_aggregation(clust, nodes.to(dtype = torch.float))
    except AttributeError: return
    x = x.to(device = "cpu")
    assert not (x - torch.tensor(non_dupl) > 10e-4).sum(-1).sum(-1)



if __name__ == "__main__":
    test_edge_feature_aggregation()
    test_edge_aggregation_nodupl()




