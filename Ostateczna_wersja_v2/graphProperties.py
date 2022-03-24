from AdditionalFunc import *


def getNodesNumber(G):
    return len(G.get_nodes())


def getEdgesNumber(G):
    return len(G.get_edges())


def getAverageDegree(G):
    # lemant o uścikach dłoni
    return (2 * len(G.get_edges()) / len(G.get_nodes()))


def getAverageNodeDegree(G, List):
    nodes_number = 0
    edges_number = 0
    nodes = G.get_nodes()
    edges = G.get_edges()
    Degress = [0] * len(List)

    avgdeg = 0
    nodeNames = []

    for i in range(0, len(List)):

        v = List[i]

        for j in range(0, len(nodes)):
            if nodes[j].get("label") == v:
                nodes_number += 1
                nodeNames.append(nodes[j].get_name())

        for j in range(0, len(nodeNames)):
            name = nodeNames[j]
            for k in range(0, len(edges)):
                e = edges[k]
                if e.get_source() == name:
                    edges_number += 1
                elif e.get_destination() == name:
                    edges_number += 1

            avgdeg += edges_number
            edges_number = 0

        if nodes_number != 0:
            # print(avgdeg)
            # print(nodes_number)
            Degress[i] = (avgdeg / nodes_number)

        avgdeg = 0
        nodes_number = 0
        nodeNames = []

    return Degress


def DFS(G):
    nodes = G.get_nodes()
    # ustaw visited na false
    for i in range(0, len(nodes)):
        nodes[i].set("visited", False)

    Component = []

    for i in range(0, len(nodes)):
        if nodes[i].get("visited") == False:
            tmp = []
            Component.append(DFSU(G, tmp, nodes[i]))

    avgEdge = getAverageEdgeComponent(G, Component)

    return len(Component), avgEdge


def DFSU(G, tmp, v):
    v.set("visited", True)
    tmp.append(v)

    edges = G.get_edges()
    # SĄSIEDNIE WIERZCHołki
    adjacentNodes = []

    for i in range(0, len(edges)):
        e = edges[i]

        if e.get_source() == v.get_name():
            if isVisited(G, e.get_destination()) == False:
                w = findNodeByName(G.get_nodes(), e.get_destination())
                adjacentNodes.append(w)
                tmp = DFSU(G, tmp, w)
        elif e.get_destination() == v.get_name():
            if isVisited(G, e.get_source()) == False:
                w = findNodeByName(G.get_nodes(), e.get_source())
                adjacentNodes.append(w)
                tmp = DFSU(G, tmp, w)

    return tmp


def isVisited(G, node):
    nodes = G.get_nodes()
    for i in range(0, len(nodes)):
        if nodes[i].get_name() == node:
            return nodes[i].get("visited")


def getAverageEdgeComponent(G, Component):
    return (len(G.get_nodes()) / len(Component))
