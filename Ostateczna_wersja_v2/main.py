from tkinter import *
from tkinter import filedialog
from PIL import Image,ImageTk
# sudo apt-get install python3-pil.imagetk
#sudo apt-get install python3-tkinter.filedialog
from datetime import datetime
from parser import *
from ProdClass import *
from DeleteCache import *
from random import randint
from graphProperties import *

import pydotplus

#globale do grafu i produkcji
global TransformationNumber,Changes, G
global MaxTransformationNumber
global ProductionList
global ChosenProduction
#globale do zapisywania obrazków
global loadname
global image_id
global GraphCanvas
global img
global imgsize
#global do statystyk
global StatisticsList

#dodatkowo w kodzie na bieżąco deklarowałem globalnie różne elementy interfejsu
#żeby funkcje zostały porpawnie wykonane

#deklaracja poczatkowych wartości
ChosenProduction=1
ProductionList=[]
MaxTransformationNumber=-1
Changes=True
TransformationNumber=0
G=None
loadname=None
StatisticsList=[]

def ExportGraphFunc():
    global G, TransformationNumber
    if G==None:
        return
    Nodes=G.get_node_list()
    Edges=G.get_edge_list()

    GExport=pydotplus.Dot(graph_type="graph")

    for N in Nodes:
        name=N.get_name()
        lbl=N.get("label")

        newnode=pydotplus.Node(name,label=lbl)
        GExport.add_node(newnode)
    for E in Edges:
        sorc=E.get_source()
        dest=E.get_destination()

        newedge=pydotplus.Edge(sorc,dest)
        GExport.add_edge(newedge)

    GExport.write("{}.{}".format("Exported"+str(TransformationNumber), 'dot'), format='dot') 

#funkcja do definiowania wierzchołków do statystyk
def DefineStatisticsListFunc():
    global StatisticsList
    InputLabels=None
    popup=Tk()
    popup.geometry("200x200")

    TextLabel=Label(popup,text="Wpisz labele wierzchołków")
    TextLabel.pack()

    NumberEntry=Entry(popup)
    NumberEntry.pack()
    def closepopup():
        global StatisticsList
        InputLabels=NumberEntry.get()
        StatisticsList=[]
        tmp=InputLabels.split(' ')
        for i in range(len(tmp)):
            StatisticsList.append(tmp[i])
        UpdateStatisticsLabel()
        popup.destroy()
        
        
        
    OKButton=Button(popup,text="OK",command=closepopup)
    OKButton.pack(side=BOTTOM)

    popup.mainloop()


def UpdateStatisticsLabel():
    global G, StatisticsLabel, StatisticsString, StatisticsList
    Gcopy=G
    StatisticsString="Statystyki\nLiczba węzłów:"
    tmp=getNodesNumber(Gcopy)
    StatisticsString+=str(tmp)+"\nLiczba krawędzi: "
    tmp=getEdgesNumber(Gcopy)
    StatisticsString+=str(tmp)+"\nLiczba składowych\nspójnych: "
    tmp,avgEdge=DFS(Gcopy)
    StatisticsString+=str(tmp)+"\nŚredni stopień\nwierzchołka:"
    tmp=getAverageDegree(Gcopy)
    tmp=round(tmp,2)
    StatisticsString+=str(tmp)+"\nŚredni stopień\nwierzchołka v\ndla v="+str(StatisticsList)+"\n"
    tmp=getAverageNodeDegree(Gcopy,StatisticsList)
    for i in range(len(tmp)):
        tmp[i]=round(tmp[i],2)
    StatisticsString+=str(tmp)+"\nŚrednia liczba węzłów\nw składowej spójnej: "
    StatisticsString+=str(avgEdge)

    StatisticsLabel.config(text=StatisticsString)


    

def PerformRandomProd(HowMany,SaveEvery):
    global ProductionList
    if HowMany>0 and len(ProductionList)>0:
        LogListBox.insert(END,"Rozpoczęto losowy ciąg "+str(HowMany)+" produkcji")
        Sequence=[]
        for i in range(HowMany):
            Sequence.append(randint(0,len(ProductionList)-1))
        PerformSequenceProd(Sequence,SaveEvery)

def PerformSequenceProd(Seq,SaveEvery):
    global G, ProductionList, ChosenProduction, MaxTransformationNumber, TransformationNumber
    ActualSeq=[]
    for P in Seq:
        try:
            num=int(P)
            if num>=0 and num<len(ProductionList):
                ChosenProduction=num
                PerformProduction(SaveEvery)
                ActualSeq.append(num)
        except ValueError:
            continue
    if G is not None:
        UpdateStatisticsLabel()
        if SaveEvery==False:
            SaveGraphPng()
            RefreshImg()
            TransformationNumber=MaxTransformationNumber
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            UpdateTransformationLabel()
            TransformationListBox.insert(END,"Transformacja "+str(TransformationNumber))
            LogListBox.insert(END,current_time+" Wykonano ciąg produkcji:"+str(ActualSeq))

#aktualizacja wartości "Wybrano transformacje"
def UpdateTransformationLabel():
    global MaxTransformationNumber
    if MaxTransformationNumber>=0:
        TransformationLabel.config(text="Wybrano Transformacje "+str(TransformationNumber))

#aktualizacja wartości "Wybrano #"
def UpdateChosenNumberLabel():
    global ChosenProduction
    ChosenNumberLabel.config(text="Wybrano #"+str(ChosenProduction))

#Do przcisku ^ przy produkcjach
def UpProdFunc():
    global ChosenProduction
    ChosenProduction-=1
    ChosenProduction=max(0,ChosenProduction)
    UpdateChosenNumberLabel() 

#Do przycisku v przy produkcjach
def DownProdFunc():
    global ChosenProduction, ProductionList
    ChosenProduction+=1
    ChosenProduction=min(ChosenProduction,len(ProductionList)-1)
    UpdateChosenNumberLabel()

#zapisz obrazek w cache
#wywołą się po każdej transformacji
#transformacja tj. jedna bądź sekwencja produkcji
def SaveGraphPng():
    global G, MaxTransformationNumber
    MaxTransformationNumber+=1
    G.write_png("cache/graf"+str(MaxTransformationNumber)+" with changes.png")
    clean_changes(G)
    G.write_png("cache/graf"+str(MaxTransformationNumber)+" clean.png")

#Wykonanie produkcji na grafie G
#Savepng to boolean, czy zapisać od razu obrazek 
def PerformProduction(SavePng):
    global G,ProductionList,ChosenProduction,MaxTransformationNumber, TransformationNumber
    if G==None:
        now = datetime.now()

        current_time = now.strftime("%H:%M:%S")
        LogListBox.insert(END,current_time+" Nie można wykonać produkcji bez wprowadzenia grafu")
        return
    if ChosenProduction!=-1 and len(ProductionList)!=0:
        performed=ProductionWithClass(G,ProductionList[ChosenProduction])
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        if SavePng:
            
            SaveGraphPng()
            TransformationNumber=MaxTransformationNumber
            RefreshImg()
            UpdateStatisticsLabel()
            UpdateTransformationLabel()
            TransformationListBox.insert(END,"Transformacja "+str(TransformationNumber))

        if performed:
            LogListBox.insert(END,current_time+" Produkcja #"+str(ChosenProduction)+" wykonano")
        else:
            LogListBox.insert(END,current_time+" Produkcja #"+str(ChosenProduction)+" nie znaleziono wierzchołka lewej strony produkcji")

#zaktualizuj listbox z produkcjami
#powinno się wywołać po każdokrotnym wczytaniu produkcji
def RefreshProductionListbox():
    global ProductionList,ProductionListbox
    ProductionListbox.delete(0,ProductionListbox.size()-1)

    for i in range(len(ProductionList)):
        #print("#"+str(i)+" ID "+str(ProductionList[i].idd))
        ProductionListbox.insert(END,"#"+str(i)+" ID "+str(ProductionList[i].idd))
    ProductionListbox.update_idletasks()
    #print(ProductionList)

def ShowHideFunc():
    global  Changes
    Changes=not(Changes)
    RefreshImg()

def RefreshImg():
    global GraphCanvas,img,imgsize, GraphImage, GraphFrame, HbarGraphFrame, VbarGraphFrame
    GenerateLoadName()
    #nie jestem pewny czy nie za dużo kodu tutaj jest,
    #w każdym razie działa
    if loadname is not None:
        GraphImage=Image.open(loadname)
        imgsize=GraphImage.size
        img=ImageTk.PhotoImage(GraphImage)
        GraphCanvas.itemconfig(image_id,image=img)
        GraphCanvas.pack(expand=True)
        GraphCanvas.place(relx=0,rely=0,width=imgsize[0],height=imgsize[1])
        VbarGraphFrame.config(command=GraphCanvas.yview)
        HbarGraphFrame.config(command=GraphCanvas.xview)
        GraphCanvas.config(xscrollcommand=HbarGraphFrame.set, yscrollcommand=VbarGraphFrame.set)

#Funkcja do "generowania" loadname
#czyli nazwy obrazka który jest w folderze cache
def GenerateLoadName():
    global TransformationNumber,Changes,loadname, MaxTransformationNumber
    if MaxTransformationNumber==-1:
        loadname="hello"
    else:
        loadname="cache/graf"+str(TransformationNumber)
        if Changes:
            loadname+=" with changes"
        else:
            loadname+=" clean"
    loadname+=".png"

#Funkcja przypisana do przycisku wykonaj losowe produkcje
#Funkcja po kliknięciu OK wywoła faktyczne produkcje na grafie
def RandomProdFunc():
    HowMany=0
    popup=Tk()
    popup.geometry("200x200")

    TextLabel=Label(popup,text="Ile?")
    TextLabel.pack()

    SaveEveryVar=BooleanVar(popup)
    SaveEveryCheckbox=Checkbutton(popup,text="Zapisać każdą produkcję?",onvalue=True,offvalue=False,variable=SaveEveryVar)
    SaveEveryCheckbox.pack()

    NumberEntry=Entry(popup)
    NumberEntry.pack()
    def closepopup():
        HowMany=NumberEntry.get()
        #print(HowMany)
        #todo
        #wywołaj w tym miejscu faktyczne wywoływanie losowych funkcji, wpisanie tablicy produkcji do loga,
        #i zapisanie grafu po
        try:
            HowMany=int(HowMany)
            PerformRandomProd(HowMany,SaveEveryVar.get())
            popup.destroy()
        except ValueError:
            popup.destroy()
        
        
    OKButton=Button(popup,text="OK",command=closepopup)
    OKButton.pack(side=BOTTOM)

    popup.mainloop()

#Funkcja przypisana do przycisku wykonaj sekwencje produkcji
#Funkcja po kliknięciu ok faktycznie wywołą produkcje na grafie   
def SequenceFunc():
    Sequence=None
    popup=Tk()
    popup.geometry("200x200")

    TextLabel=Label(popup,text="Wprowadź sekwencję\n oddzieloną spacjami")
    TextLabel.pack()

    
    SaveEveryVar=BooleanVar(popup)
    SaveEveryCheckbox=Checkbutton(popup,text="Zapisać każdą produkcję?",onvalue=True,offvalue=False,variable=SaveEveryVar)
    SaveEveryCheckbox.pack()

    NumberEntry=Entry(popup)
    NumberEntry.pack()
    def closepopup():
        
        Sequence=NumberEntry.get().split(" ")
        PerformSequenceProd(Sequence,SaveEveryVar.get())
        #todo
        #wywołaj w tym miejscu faktyczne wywoływanie sekwencji produkcji,
        #i zapisanie grafu po
        popup.destroy()
    
    OKButton=Button(popup,text="OK",command=closepopup)
    OKButton.pack(side=BOTTOM)

    popup.mainloop()

#Funkcja przypisana do przycisku wczytaj graf
def LoadGraphFunc():
    global G
    def browseFiles(): 
        global G
        filename = filedialog.askopenfilename(initialdir = "/", 
        title = "Select a File", 
        filetypes = (("Pliki dot", "*.dot*"), ("Wszystkie pliki", "*.*")))
        if type(filename) is str:
            G = pydotplus.graph_from_dot_file(filename)
            #nodeLabeling(G,0)
            edgeLabeling(G)
            SaveGraphPng()
            #print("hooray")
            now = datetime.now()
            UpdateStatisticsLabel()
            current_time = now.strftime("%H:%M:%S")
            LogListBox.insert(END,current_time+" Graf wczytany poprawnie")
            label_file_explorer.configure(text="File Opened: "+filename) 
    def closepopup():
        #todo
        #wywołaj w tym miejscu faktyczne wczytanie grafu
        #i zapisanie grafu po
        #SaveGraphPng()
        TransformationListBox.insert(END,"Transformacja "+str(TransformationNumber))
        RefreshImg()
        popup.destroy()
    popup=Tk()
    popup.geometry("200x200")
    OKButton=Button(popup,command=closepopup,text="OK")
    OKButton.pack(side=BOTTOM)


    label_file_explorer = Label(popup,  
                            text = "File Explorer using Tkinter", 
                            width = 100, height = 4,  
                            fg = "blue")
    label_file_explorer.pack() 

    button_explore = Button(popup,  
                        text = "Browse Files", 
                        command = browseFiles)
    button_explore.pack()  

    popup.mainloop()
    
       
    # Change label contents 

#Funkcja przypisana do przycisku wczytaj produkcje
def LoadProdFunc():
    global ProductionList
    def browseFiles(): 
        filename = filedialog.askopenfilename(initialdir = "/", 
        title = "Select a File", 
        filetypes = (("Pliki txt", "*.txt*"), ("Wszystkie pliki", "*.*")))
        if type(filename) is str:
            label_file_explorer.configure(text="File Opened: "+filename)
            parser(ProductionList,filename) 
    def closepopup():
        UpdateChosenNumberLabel()
        RefreshProductionListbox()
        popup.destroy()
    popup=Tk()
    popup.geometry("200x200")
    OKButton=Button(popup,command=closepopup,text="OK")
    OKButton.pack(side=BOTTOM)


    label_file_explorer = Label(popup,  
                            text = "File Explorer using Tkinter", 
                            width = 100, height = 4,  
                            fg = "blue")
    label_file_explorer.pack() 

    button_explore = Button(popup,  
                        text = "Browse Files", 
                        command = browseFiles)
    button_explore.pack()  

    popup.mainloop()

#Do przycisku przy liście transformacj
def DownButtonFunc():
    global TransformationNumber
    TransformationNumber+=1
    TransformationNumber=min(MaxTransformationNumber,TransformationNumber)

    RefreshImg()
    UpdateTransformationLabel()

#do przycisku przy liście transformacji
def UpButtonFunc():
    global TransformationNumber
    TransformationNumber-=1
    TransformationNumber=max(0,TransformationNumber)
    RefreshImg()
    UpdateTransformationLabel()


root=Tk()

#minimalny rozmiar roota
minsize1=1200
minsize2=1200

root.minsize(minsize1,minsize2)


#lewa ramka, tam znajdują się okienko z produkcjami (ze scrollem) i przyciski do produkcji
LeftFrame=Frame(root,bg="lightblue")
LeftFrame.pack()
LeftFrame.place(relx=0,relwidth=0.15,relheight=1.0,rely=0)

#przyciski w LeftFrame

LoadGraphButton=Button(LeftFrame,text="Wczytaj graf",height=2,width=20,command=LoadGraphFunc,padx=5,pady=5)
LoadGraphButton.pack()

LoadProductionButton=Button(LeftFrame,text="Wczytaj produkcje",height=2,width=20,command=LoadProdFunc,padx=5,pady=5)
LoadProductionButton.pack()

ShowHideChangesButton=Button(LeftFrame,text="Pokaż/Ukryj zmiany",height=2,width=20,command=ShowHideFunc,padx=5,pady=5)
ShowHideChangesButton.pack()

DoProductionButton=Button(LeftFrame,text="Wykonaj produkcję",height=2,width=20,command=lambda: PerformProduction(True),padx=5,pady=5)
DoProductionButton.pack()

DoRandomProductionsButton=Button(LeftFrame,text="Wykonaj losowe\n produkcje",height=4,width=20,command=RandomProdFunc,padx=5,pady=5)
DoRandomProductionsButton.pack()

SequenceOfProductionsButton=Button(LeftFrame,text="Wykonaj sekwencje\n produkcji",height=4,width=20,command=SequenceFunc,padx=5,pady=5)
SequenceOfProductionsButton.pack()

RefreshCanvasButton=Button(LeftFrame,text="Odśwież obrazek",command=RefreshImg,height=2,width=20,padx=5,pady=5)
RefreshCanvasButton.pack()

DefineStatisticsLabelsButton=Button(LeftFrame,text="Zdefiniuj wierzchołki\n do statystyk",command=DefineStatisticsListFunc,height=4,width=20,padx=5,pady=5)
DefineStatisticsLabelsButton.pack()


ChosenNumberLabel=Label(text="Nie wybrano\n produkcji")
ChosenNumberLabel.place(relx=0,rely=0.55)

UpProdButton=Button(LeftFrame,text="/ \\\n|",command=UpProdFunc)
UpProdButton.place(relx=0.7,rely=0.50)

DownProdButton=Button(LeftFrame,text="|\n\\ /",command=DownProdFunc)
#DownProdButton.pack()
DownProdButton.place(relx=0.7,rely=0.55)

ExportGraphButton=Button(LeftFrame,text="Eksportuj graf",command=ExportGraphFunc,height=2,width=20,padx=5,pady=5)
ExportGraphButton.pack()

#Listbox z produkcjami (nie mylić z ProductionList)
#czyli wylistowane produkcje po numerze # oraz id produkcji wczytanym z plikus
global ProductionListbox
ProductionListbox=Listbox(LeftFrame,highlightcolor="grey",selectmode=SINGLE)
ProductionListbox.pack(side=BOTTOM)
ProductionListbox.place(relwidth=1,relheight=0.4,rely=0.6)

#Scroll do listy produkcji
ProductionListScrollbar=Scrollbar(ProductionListbox)

ProductionListbox.config(yscrollcommand=ProductionListScrollbar.set)


RefreshProductionListbox()

ProductionListScrollbar.config=ProductionListbox.yview



#ramka centralna przeznaczona na graf
GraphFrame=Frame(root,bg="white")
GraphFrame.pack()
GraphFrame.place(relx=0.15,rely=0,relwidth=0.7,relheight=0.8)
#canvas na obrazek z grafem

GraphCanvas=Canvas(GraphFrame,bg="white")
GraphCanvas.pack(expand=True)
GraphCanvas.place(relx=0,rely=0)

global HbarGraphFrame,VbarGraphFrame

#scrollbary do graphframe, ze stack overflow
HbarGraphFrame=Scrollbar(GraphFrame,orient=HORIZONTAL,command=GraphCanvas.yview)
HbarGraphFrame.pack(side=BOTTOM,fill=X)
HbarGraphFrame.config(command=GraphCanvas.xview)
VbarGraphFrame=Scrollbar(GraphFrame,orient=VERTICAL,command=GraphCanvas.xview)
VbarGraphFrame.pack(side=RIGHT,fill=Y)
VbarGraphFrame.config(command=GraphCanvas.yview)
GraphCanvas.config(xscrollcommand=HbarGraphFrame.set, yscrollcommand=VbarGraphFrame.set)


global GraphImage
#wczytywanie pliku z grafem
GraphImage=Image.open('hello.png')
imgsize=GraphImage.size
img=ImageTk.PhotoImage(GraphImage)
image_id=GraphCanvas.create_image(0,0,anchor=NW,image=img)


#prawa ramka, tu będą statystyki
RightFrame=Frame(root,bg="lightblue")
RightFrame.pack()
RightFrame.place(relx=0.85,relwidth=0.15,relheight=1.0)

global StatisticsString
StatisticsString="""Statystyki\n
Liczba węzłów: brak\n
Liczba krawędzi: brak\n
Liczba składowych\nspójnych: brak\n
Średni stopień\nwierzchołka: brak\n
Średni stopień\nwierzchołka v\ndla v=[]: brak\n
Średnia liczba węzłów\nw składowej spójnej: brak\n
"""
global StatisticsLabel
StatisticsLabel=Label(RightFrame,text=StatisticsString,justify=LEFT)
StatisticsLabel.place(relx=0,rely=0,relwidth=1.0)

#załadowanie legendy
legendimage=Image.open('legend.png')
legendimage=legendimage.resize((180,180), Image.ANTIALIAS)
legendimg=ImageTk.PhotoImage(legendimage)
LegendCanvas=Canvas(RightFrame,bg="lightblue")
LegendCanvas.create_image(0,0,anchor=NW,image=legendimg)
LegendCanvas.place(relx=0.0,rely=0.5)


#dolna centralna ramka
#tam jest lista transformacji
#i log
MiddlebottomFrame=Frame(root,bg="lightblue")
MiddlebottomFrame.pack()
MiddlebottomFrame.place(relx=0.15,rely=0.8,relwidth=0.7,relheight=0.2)

#Lista Transformacji

TransformationLabel=Label(MiddlebottomFrame,text="Brak transformacji")
TransformationLabel.place(relx=0,rely=0)

TransformationListBox=Listbox(MiddlebottomFrame,highlightcolor="grey",selectmode=SINGLE,height=10)
TransformationListBox.pack()
TransformationListBox.place(relx=0,rely=0.2,relheight=0.8,relwidth=0.3)

TransformationListBoxScrollbar=Scrollbar(TransformationListBox)
TransformationListBox.config(yscrollcommand=TransformationListBoxScrollbar)
TransformationListBoxScrollbar.config=TransformationListBox.yview

#Log

LogListBox=Listbox(MiddlebottomFrame,highlightcolor="grey",selectmode=SINGLE)
LogListBox.place(relwidth=0.5,relx=0.5,relheight=1.0)
LogListBoxScrollbar=Scrollbar(LogListBox)

LogListBox.config(yscrollcommand=LogListBoxScrollbar)

LogListBoxScrollbar.config=LogListBox.yview



#Przyciski do MiddlebottomFrame

UpButton=Button(MiddlebottomFrame,text="/ \\\n|",command=UpButtonFunc)
UpButton.pack()
UpButton.place(relx=0.4,rely=0.4)

DownButton=Button(MiddlebottomFrame,text="|\n\\ /",command=DownButtonFunc)
DownButton.pack()
DownButton.place(relx=0.4,rely=0.6)

root.mainloop()

#usuwa wszystko w folderze cache
DeleteCache()
