


import numpy as np
from scipy.spatial import Delaunay
from tqdm import tqdm
import laspy
import pyvista
import trimesh
import pyrender
from shapely.geometry import Point, Polygon
import matplotlib.pyplot as plt

def OrderSelector(l):
    if l[0]==l[-1]:
        return [l[0],l[-1],l[1],l[2]]
    return [l[1],l[2],l[0],l[3]]
    
def distance(p1, p2):
    return np.linalg.norm(p1-p2)


def circumferance(triangle):
    return (distance(triangle[1], triangle[2])+distance(triangle[2], triangle[0])+distance(triangle[0], triangle[1]))


def add2Dict(d,v):
    key = str(np.round(v[0]))+"|"+str(np.round(v[1]))
    if key not in d.keys():
        d[key] = [v]
    else:
        d[key].append(v)

def upTheLower(bound,e):
    if e < bound:
        return bound
    return e

def calculate_z_score(data):
    if len(data) <2:
        return(np.zeros(len(data)))
    mean = np.mean(data)

    std_dev = np.std(data)
    if std_dev ==0:
        return (np.zeros(len(data)))
    z_scores = (data - mean) / std_dev
    return z_scores


def create_string(e):
    s = np.sort(e)
    return str(s[0])+"!"+str(s[1])
    

def returnEdges(v):

    return [[v[0], v[1]],
            [v[1], v[2]],
            [v[2], v[0]]]


def returnUniqueEdges(edgeLord):
    stringArray =np.array([create_string(e) for e in edgeLord])
    v,c = np.unique(stringArray, return_counts=True)
    uniques = v[c<2]
    sorter = np.argsort(stringArray)
    indexesForUniques  = sorter[np.searchsorted(stringArray,uniques, sorter=sorter)]
    return edgeLord[indexesForUniques]



class mesh3d:
    def __init__(self, filenameList,maxEast= np.Inf, minEast=-np.Inf, maxNorth = np.Inf, minNorth= -np.Inf, sl=0):
        self.sea_points = np.array([[maxEast, maxNorth, sl], [maxEast, minNorth, sl], [minEast, maxNorth, sl], [minEast, minNorth, sl]])
        self.sea_mesh  = Delaunay(self.sea_points[:,:2]-self.sea_points[:,:2].mean(axis=0)).simplices
        self.points = self.LoadAndCrop(filenameList=filenameList, maxEast=maxEast,minEast=minEast, maxNorth=maxNorth,minNorth=minNorth)
        self.sea_level_of_pc = self.remove_bottom_part(110)
     
        self.OutlierZDeviationFilter()
        self.edges = Delaunay(self.points[:,:2]-self.points[:,:2].mean(axis=0)).simplices
        print("3D Mesh created")

    def LoadAndCrop(self,filenameList, maxEast= np.Inf, minEast=-np.Inf, maxNorth = np.Inf, minNorth= -np.Inf):
        xyz = np.array([[0,0,0]])
        for fn in filenameList:
            a = laspy.read(fn).xyz
            xyz = np.append(xyz, a, axis = 0)
            print(len(xyz))
            print(f"Read In {fn}")
        xyz = np.delete(xyz, 0,0)
        
        print(f'Cropping North between {minNorth} and {maxNorth} and East between {minEast} and {maxEast}')
        
        xyz = np.array([e for e in tqdm(xyz) if maxEast>= e[0]])
        xyz = np.array([e for e in tqdm(xyz) if e[0]>= minEast])
        
       
        xyz = np.array([e for e in tqdm(xyz) if e[1]>= minNorth])
        xyz = np.array([e for e in tqdm(xyz) if maxNorth>=e[1]])
        return xyz 

    def remove_bottom_part(self, number_of_points_for_lower_limit = 150):
     
        v, c   = np.unique(self.points[:,2], return_counts=True)
        
        i = next(i for i in range(len(c)) if c[i]>number_of_points_for_lower_limit)
        bottom_limit = v[i]
        print(f'bottom_level Is {bottom_limit}')
        self.points = np.array([e for e in tqdm(self.points) if e[2]>= bottom_limit+0.05])
        return bottom_limit


    def addSeaMesh_toPoints(self):
        l = len(self.points)

        self.points = np.append(self.points, self.sea_points, axis = 0)
        self.sea_mesh = np.array([np.array(e)+l for e in self.sea_mesh])
        



    def edgesort_mesh(self, lim, sl, b = None):
        
        self.points = np.array([e for e in self.points if e[2]>= sl])
        self.edges = Delaunay(self.points[:,:2]-self.points[:,:2].mean(axis=0)).simplices
        
        simplices_circuferance = np.array([circumferance(self.points[t]) for t in self.edges])
        print("finding ok simplexes")
        restricted_edges = np.array([self.edges[i] for i in tqdm(range(len(simplices_circuferance))) if simplices_circuferance[i]< lim])
        edges = np.reshape(np.reshape(np.array([returnEdges(e) for e in tqdm(restricted_edges)]),-1), (-1,2))
        unixes = returnUniqueEdges(edges)
        v,c = np.unique(np.reshape(unixes, -1), return_counts= True)
        new_ponts =  np.array([[e[0],e[1],sl-1] for e in self.points[v]])

        idx_correspondence= np.arange(len(self.points),len(unixes)+len(self.points))


        self.points  = np.append(self.points, new_ponts, axis = 0)

        idx_dict= dict()
        for i in range(len(v)):
            idx_dict[v[i]]= idx_correspondence[i]


        new_simplexes = np.array([np.array([[idx_dict[e[0]], idx_dict[e[1]], e[1]], [idx_dict[e[0]], e[1], e[0]]]) for e in tqdm(unixes)])
     
            
        restricted_edges = np.append(restricted_edges,np.reshape(new_simplexes,(-1,3)), axis = 0) 

        
        self.edges = restricted_edges


        if b != None:
            for poly in b:
                np.array(poly.exterio)

    


    def show_point_cloud(self):
        pc = pyvista.PolyData(self.points)
        pc.plot(eye_dome_lighting = True)



    def OutlierZDeviationFilter(self):

        temp_dict = dict()
        [add2Dict(temp_dict, e) for e in tqdm(self.points)]
        temp = np.array([np.array([0,0,0])])
        for values in tqdm(temp_dict.values()):
            z_scores = calculate_z_score(np.array(values)[:,2])
            temp = np.append(temp,np.array([e for e, z in zip(values, z_scores) if z < 1.6]), axis =0)
        self.points = np.delete(temp, 0,0)
    
        
      
    
    def findEdgesCrossing(self, t, sl):
        p = self.points[t]
        return [[i,i-1] for i in range(len(p)) if np.sign(p[i][2]-sl) !=np.sign(p[i-1][2]-sl)]
    

    def separateLandAndSeaMesh(self, sl):
        print("Separating ocean from Land")
        terrain = np.array([t for t in tqdm(self.edges) if  np.any(self.points[t][:,2]>sl)])
        sea = np.array([t for t in tqdm(self.edges) if np.all(self.points[t][:,2]==sl)])
        return terrain, sea
    


    def cutToSealevel(self, sl):
        print("Cutting Mesh 3d")
        unaffectedTriangles = np.array([t for t in tqdm(self.edges) if self.pointsSeparatedOnHeight(t=t,sep = sl)])
        relevantTriangles = np.array([t for t in tqdm(self.edges) if not self.pointsSeparatedOnHeight(t=t,sep = sl)])
        edgesCrossingSL = np.array([self.findEdgesCrossing(t=t, sl = sl) for t in tqdm(relevantTriangles)])
        edgesCrossingSL_Reshaped = np.reshape(edgesCrossingSL, len(relevantTriangles)*4)
        edgecrossingsSL1 =np.array([[relevantTriangles[i][edgesCrossingSL_Reshaped[4*i:4*i+2]],relevantTriangles[i][edgesCrossingSL_Reshaped[4*i+2:4*i+4]]]for i in range(len(relevantTriangles))])
        newPoints = np.array([p[0]+(p[1]-p[0])*((sl-p[0][2])/(p[1][2]-p[0][2])) for p in tqdm(np.reshape(self.points[edgecrossingsSL1], (len(edgesCrossingSL)*2,2,-1)))])

        uniquePoints = np.unique(newPoints, axis = 0)
        newPointsIdx = np.array([len(self.points)+i for i in tqdm(range(len(uniquePoints)))])
        reshaper = np.array([OrderSelector(e) for e in np.reshape(edgecrossingsSL1,(len(edgecrossingsSL1),-1))])
        
        d = dict()
        for i in tqdm(range(len(newPointsIdx))):
            d[str(uniquePoints[i])] = newPointsIdx[i]

        newTriangles = np.array([[[d[str(newPoints[2*i:2*i+2][0])],d[str(newPoints[2*i:2*i+2][1])],reshaper[i][0]],
                                [d[str(newPoints[2*i:2*i+2][0])], d[str(newPoints[2*i:2*i+2][1])],reshaper[i][-1]],
                                [d[str(newPoints[2*i:2*i+2][0])],reshaper[i][-1], reshaper[i][-2]]
                                ] for i in tqdm(range(len(relevantTriangles)))])
        
        newTriangles = np.reshape(newTriangles, (len(relevantTriangles)*3,3))
        try:
            self.edges = np.append(unaffectedTriangles, newTriangles, axis = 0)
        except:
            self.edges = newTriangles

        self.points = np.append(self.points,uniquePoints, axis = 0)
        self.points = np.array([[p[0],p[1],upTheLower(sl, p[2])] for p in tqdm(self.points)])
        

    def pointsSeparatedOnHeight(self,t,sep):
        pointsbyZ = self.points[t][:,2]
        return (len([e for e in pointsbyZ if e >sep])*len([e for e in pointsbyZ if e < sep]))==0
    




        
        