from AdditionalFunc import *
import pydotplus


class ProductionClass():
    LEFT = [] # wierzchołki emedded
    LEFT2 = None # wierzchołek lewej strony produkcji
    RIGHT= [] # prawe wierzchołki embedded 
    RightSideG = None # tworzony graf 
    idd = None # id produkcji
    def __init__( self,RightSideG,idd,LEFT2,EmbeddingArray):

        self.LEFT = []
        self.RIGHT= []

        edgeLabeling(RightSideG)
        self.idd = idd
        self.RightSideG=RightSideG
        self.LEFT2 = LEFT2

        for i in range(len(EmbeddingArray)):
            self.LEFT.append(EmbeddingArray[i][0])
            self.RIGHT.append(EmbeddingArray[i][1])


    def info(self):
        return self.LEFT,self.RIGHT


#prodclass teraz zwraca True jeśli znaleziono wierzchołek lewej strony
#zwraca false wpp
def ProductionWithClass(G,Prod):
    #zbieranie informacji o grafie do zmiennych
    clean_changes(G)
    
    #Graf prawej strony produkcji
    RightSideG=Prod.RightSideG
    #i informacje na temat transformacji osadzenia
    LEFT,RIGHT=Prod.info()

    nodes=G.get_nodes()
    edges=G.get_edge_list()
    node_number=len(nodes)
    edge_number=len(edges)
    
    
    #znajdz wierzcholek lewej strony produkcji
    LeftNode = findNodeByLabel(nodes,Prod.LEFT2)
    if LeftNode == None:
        #print ("Nie znaleziono wierzchołka lewej strony produkcji.")
        return False

    LeftNodeName = LeftNode.get_name() # imie 
    LeftConNodes = [] # wierzchołki odłączone od X

    # odłaczamy wierzchołki i dodajemy do tablicy
    deleting_edges(G,nodes,edges,LEFT,LeftConNodes,LeftNodeName)

    RightConNodes = [] # tablica nowych wierzchołkow
    #RightConNodes.append(LeftNode)

    #Dodaj graf prawej strony produkcji do grafu G
    #przy okazji zapisz w tablicy dodane wierzchołki
    AddRightProductionSide(G,RightSideG,RightConNodes)

    #Wierzchołek lewej strony produkcji jest do usunięcia
    LeftNode.set("color","red")

    #embedding
    embedding(G,LeftConNodes,RightConNodes,LEFT,RIGHT)
    return True
    
def deleting_edges(G,nodes,edges,LEFT,LeftConNodes,LeftNodeName):
    edge_number=len(edges)
    for j in range (0,len(LEFT)):
        
        Prod_label = LEFT[j]
        
        for i in range (0,edge_number):
            
            src = edges[i].get_source()
            dst = edges[i].get("dest")
            
            if ((src == LeftNodeName and dst == Prod_label) ):
                
                #zamiast usuwać dajemy kolor czerwony
                LeftConNodes.append(findNodeByName(nodes,str(edges[i].get_destination())))
                edges[i].set("color","red")

            src = edges[i].get("sorc")
            dst = edges[i].get_destination()               
            if (src == Prod_label and dst == LeftNodeName ):
                
                #zamiast usuwać dajemy kolor czerwony
                LeftConNodes.append(findNodeByName(nodes,str(edges[i].get_source())))
                edges[i].set("color","red")

                
#przypinanie krawędzi
def embedding(G,LeftConNodes,RightConNodes,LEFT,RIGHT):
    for i in range (0,len(LeftConNodes)):
        for j in range (0,len(LEFT)):
            
            if LeftConNodes[i].get("label") == LEFT[j]:
                
                for k in range (0,len(RightConNodes)):
                    
                    if RightConNodes[k].get("label") == RIGHT[j]:
                        
                        G.add_edge(pydotplus.Edge(LeftConNodes[i].get_name(),RightConNodes[k].get_name(),sorc = LEFT[j], dest = RIGHT[j],color="green"))



#dodaj graf prawej strony produkcji
#i dodaj wierzchołki do tablicy wierzchołków prawej strony produkcji
def AddRightProductionSide(G,RightSideG,RightConNodes):
    
    #wierzchołki prawej strony produkcji
    Nodes=RightSideG.get_nodes()
    
    #zapisuj labele prawej strony produkcji w tablicy
    NodeLabels=[]

    #zapisuj imiona (indeksy) prawej strony produkcji w tablicy
    IndexesOfAddedNodes=[]


    #dodaj do G nowe wierzchołki
    for i in range(len(Nodes)):

        lbl=Nodes[i].get("label")
        NodeLabels.append(lbl)

        newnodeidx=str(nextfreeidx(G))

        IndexesOfAddedNodes.append(newnodeidx)
        newnode=pydotplus.Node(newnodeidx,color="green",label=lbl)
        RightConNodes.append(newnode)
        G.add_node(newnode)
        
    #krawędzie grafu prawej strony produkcji
    Edges=RightSideG.get_edge_list()

    for E in Edges:

        source=E.get_source()
        destination=E.get_destination()

        for i in range(len(Nodes)):

            if source==Nodes[i].get_name():
                
                for j in range(len(Nodes)):

                    if destination==Nodes[j].get_name():
                        #dodaj do G krawędzie z prawej strony produkcji
                        G.add_edge(pydotplus.Edge(IndexesOfAddedNodes[i],
                        IndexesOfAddedNodes[j],
                        color="green",
                        sorc=NodeLabels[i],
                        dest=NodeLabels[j]))
            


#zwróć następny wolny indeks w grafie
def nextfreeidx(G):
    Vertices=G.get_node_list()
    indexes=[]
    n=len(Vertices)
    for i in range(n):
        indexes.append(int(Vertices[i].get_name()))
    return max(indexes)+1
