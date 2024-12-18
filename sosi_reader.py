import string
import chardet
from pathlib import Path
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon
p = Path(__file__).parent
import scipy as sci

sosfilePath = p / 'files_input'/'Ravnkloa'/'SOSI'

def withinFrame(N_min,E_min, N_max, E_max, crds):
    return (N_min <= crds[0] <= N_max) and (E_min <= crds[1]<= E_max)

def num_dots_line(line):
    for i in range(len(line)):
        if line[i] != ".":
            return i

def get_contents_between_n_dots(n_dots,content):
    line_index = [idx for idx, e in enumerate(content) if num_dots_line(e)==n_dots]
    return line_index

def create_sub_order(l):
    l = list(dict.fromkeys(l))
    indexes = get_contents_between_n_dots(2, l)

    keys = np.array(l)[indexes]
    indexes.append(-1)
    l.append("bs")
    values = [l[indexes[i]+1:indexes[i+1]] for i in range(len(indexes)-1)]
    if "NØ" in keys[-1]:
        values[-1] = np.array([e.split(" ")[:2] for e in values[-1]],dtype = np.float64)/10000
        keys[-1] = "..NØ"

    mydict = dict()
    for i in range(len(keys)):
        if not list(values[i]):
            k = keys[i][2:].split(" ")
            mydict[k[0]] = k[1]
        else:
            mydict[keys[i][2:]]= values[i]



    return mydict


class SOSI:
    def __init__(self, filename,maxO, minO, maxN, minN):
        self.sosi_dict = dict()
        self.obj_typeDict = dict()
        self.brygger = []
        self.filename = filename
        self.head, self.contents = self.SOSI_Reader()
        self.cut_and_limit(N_min=minN, E_min=minO, E_max=maxO, N_max=maxN)
        self.polygon_creator()
        
        
        
    def cut_and_limit(self,N_min, E_min, N_max, E_max):

        temp_dict  = dict()
        for key, values in tqdm(self.contents.items()):
            temp_dict[key] = list()
            
            for e in values:
                crds = np.array(e["NØ"])
                if any([N_min <= c[0] <= N_max and E_min <= c[1] <= E_max for c in crds]):
                    temp_dict[key].append(e)
        [temp_dict.pop(key) for key in list(temp_dict.keys()) if len(temp_dict[key]) == 0]
        self.contents = temp_dict
        del temp_dict
        
    def dict_append(self, key, content):
        self.sosi_dict[key] = content


    def SOSI_Reader(self):
        
        with open(self.filename, "r", encoding="utf-8-sig") as sosi_file:
            lines = sosi_file.readlines()
            lines = [e.strip() for e in lines]

            idxes = get_contents_between_n_dots(1,lines)
            contents = [lines[idxes[i]:idxes[i+1]] for i in range(len(idxes)-1)]
            [self.dict_append(e[0], e[1:]) for e in contents]
            key_list = list(self.sosi_dict.keys())
            dict_list = [create_sub_order(self.sosi_dict[key_list[i]]) for i in range(len(key_list))]

            sosiTypes = list(set([e["OBJTYPE"] for e in dict_list if "OBJTYPE" in list(e.keys())]))
            newDict = dict()
            for e in sosiTypes:
                newDict[e] = []
            [newDict[e["OBJTYPE"]].append(e) for e in dict_list[1:]]
            return dict_list[0], newDict
            
    def polygon_creator(self):
        acceptable_items = ["Flytebrygge", "Flateavgrensning"]
        try:
            flytebrygger  = [np.transpose(v["NØ"][:,[1,0]]) for v in self.contents[acceptable_items[0]]]
            flater= [np.transpose(v["NØ"][:,[1,0]]) for v in self.contents[acceptable_items[1]]]
            avgPoints = [np.average(f, axis = 1) for f in flater]
            punktTilBrygge = [np.argmin([np.linalg.norm(np.reshape(fb, -1)-avgp) for avgp in avgPoints]) for fb in flytebrygger]
            self.brygger = [Polygon(np.transpose(flater[punktTilBrygge[i]])) for i in range(len(flytebrygger))]
        except:
            self.brygger = []


    def plotKai(self, k ="KaiBryggeKant" ):
        key = k
        fig = plt.figure()
        ax = fig.add_subplot()

        for v in self.contents[key]:
            a = np.transpose(v["NØ"])
            plt.plot(a[1], a[0])
            


        ax.set_aspect('equal', adjustable='box')
        plt.show() 

    def plot_lines(self):

        acceptable_items = ["Flytebrygge", "Flateavgrensning"]
        fig = plt.figure()
        ax = fig.add_subplot()
        flytebrygger  = []

        flater= []
        colours = ["r", "g", "b"]

        avgensning_flytebrygger  = []
        for v in self.contents[acceptable_items[0]]: #flytebrygge
            flytebrygger.append(np.transpose(v["NØ"][:,[1,0]]))

        for v in self.contents[acceptable_items[1]]: #avgensning
            flater.append(np.transpose(v["NØ"][:,[1,0]]))

        avgPoints = [np.average(f, axis = 1) for f in flater]
        for fb in flytebrygger:
            avgensning_flytebrygger.append(np.argmin([np.linalg.norm(np.reshape(fb, -1)-avgp) for avgp in avgPoints]))
            
    

        
        for i in range(len(flytebrygger)):
            b = flytebrygger[i]
            flate = flater[avgensning_flytebrygger[i]]
            self.brygger.append(Polygon(np.transpose(flate)))
            
            flate = np.append(flate, np.reshape(flate[:,0], (2,-1)), axis = 1)
            plt.plot(b[0], b[1], color =colours[i%3], marker ='o')
            plt.plot(flate[0], flate[1], color = colours[i%3])
            
            

        ax.set_aspect('equal', adjustable='box')
        plt.show()  
                
        

    def calculatePointInsideBrygge(self, point):
        p = Point(point)
        for f in self.brygger:
            if p.within(f): return True
        return False
        #https://stackoverflow.com/questions/16625507/checking-if-a-point-is-inside-a-polygon/23453678#23453678
        
        
        
        

        

            


            

maxN = 7034771.04
maxE = 569538.67
minN = 7034672.99
minE = 569471.56

if __name__ == "__main__":
    sosi = SOSI(sosfilePath/"32_N5_5001_Bygg_og_Anlegg.SOS", maxO=maxE, maxN=maxN, minO=minE, minN=minN)
    

    sosi.plotKai()
    sosi.plot_lines()
    print(sosi.calculatePointInsideBrygge([569528.67,7034751.04]))


