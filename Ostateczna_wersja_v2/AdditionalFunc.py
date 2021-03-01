from PIL import Image
import pydotplus
import os

def findNodeByName(nodes,name):
    for i in range (0,len(nodes)):
        if nodes[i].get_name() == name:
            return nodes[i]
    return None

def findNodeByLabel(nodes,name):
    for i in range (0,len(nodes)):
        if nodes[i].get("label") == name:
            return nodes[i]
    return None

#not used in final product
def VisualizeWithLegend(G):

    legend=Image.open('legenda.png')
    legend_size=legend.size

    G.write_png('graf.png')

    GraphImg=Image.open('graf.png')

    G_size=GraphImg.size

    new_image = Image.new('RGB',(max(legend_size[0],G_size[0]),G_size[1]+legend_size[1] ), (250,250,250))

    new_image.paste(GraphImg,(0,0))
    new_image.paste(legend, (0,G_size[1]))

    os.remove('graf.png')
    #new_image.save('graf with legend.png')
    return new_image
    #new_image.show()

def clean_changes(G):
    nodes=G.get_node_list()
    edges=G.get_edge_list()
    node_number=len(nodes)
    edge_number=len(edges)
    for i in range(edge_number):
        col=edges[i].get("color")
        if col=="red":
            G.del_edge(edges[i].get_source(),edges[i].get_destination())
        elif col=="green":
            edges[i].set("color","black")
    for i in range(node_number):
        col=nodes[i].get("color")
        if col=="green":
            nodes[i].set("color","black")
        elif col=="red":
            G.del_node(nodes[i].get_name())
    
    

def edgeLabeling(G):
    E = G.get_edges()
    N = G.get_nodes()
    for i in range (0,len(E)):
        sorc = findNodeByName(N,E[i].get_source()).get("label")
        dest = findNodeByName(N,E[i].get_destination()).get("label")
        E[i].set("sorc",sorc)
        E[i].set("dest", dest)

def nodeLabeling(G,node_number):
    nodes = G.get_nodes()
    edges = G.get_edges()
    oldNames = []
    newNames = []
    for i in range (0,len(nodes)):

        name = nodes[i].get_name()
        index  = str(node_number)

        newnode=pydotplus.Node(index)
        newnode.set("label",name)

        G.del_node(name)

        G.add_node(newnode)

        oldNames.append(name)
        newNames.append(index)        


        node_number +=1
    for i in range (0,len(edges)):
        edge = edges[i]
        sorc = None
        dest = None
        for j in range (0,len(oldNames)):
            name = oldNames[j]
            if edges[i].get_destination() == name: 
                dest = newNames[j]
            elif edges[i].get_source() == name: 
                sorc = newNames[j]  

        G.add_edge(pydotplus.Edge(sorc ,dest))
        edge.set("toDelete",True)
    for i in range (0,len(edges)):
        if edges[i].get("toDelete") != None:
            G.del_edge(edges[i].get_source(),edges[i].get_destination())
    return node_number

