import pydotplus

from ProdClass import *


def parseProductions(P, filename):
    idd = None
    Left = None
    newfile = []
    fileIndex = 0
    embeddedArray = []
    # 0 - szukanie new line'ow
    # 1 - szukanie id produkcji
    # 2 - szukanie grafu lewej strony
    # 3 - szukanie grafu prawej strony
    # 4 - szukanie transformacji osadzenia
    phase = 1
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()

            if line != '\n' and line != '':
                if line.find('#') != -1:
                    if phase == 4:
                        #
                        newfile2 = "".join(newfile)
                        graphname = "cache/grap" + str(fileIndex) + ".dot"
                        grap = open(graphname, 'w')
                        grap.write(newfile2)
                        grap.close()
                        #
                        fileIndex += 1
                        newfile = []
                        addProduction(P, idd, Left, graphname, embeddedArray)
                        embeddedArray = []
                        #
                    phase = (phase) % 4 + 1
                elif phase == 1:
                    idd = line
                elif phase == 2:
                    Left = line
                elif phase == 3:
                    newfile.append(line)
                elif phase == 4:
                    embeddedArray.append(line)
    # print (idd)
    # print (Left)
    # print (newfile)
    # print (embeddedArray)
    f.close()


def addProduction(P, idd, Left, graphname, embedded):
    GG = pydotplus.graph_from_dot_file(graphname)

    P.append(ProductionClass(GG, idd, Left, parseEmbedding(embedded)))


def parseEmbedding(embedded):
    # print(embedded)
    for i in range(0, len(embedded)):
        # print(embedded[i])
        embedded[i] = "".join(embedded[i].split())
    # print(embedded)
    return embedded
