import numpy as np
from tqdm import tqdm
from pathlib import Path

import ortophoto
import API
import mesh as mesh
from PIL import Image
import gltf
import sosi_reader
import datetime
import os

p = Path(__file__).parent




def pyCoast(foldername, max_east: float, min_east: float, max_north: float, min_north:float,
            date: datetime.datetime, sosi_file_recognizer: str = "Bygg_og_Anlegg.SOS"):
    center_point = ((max_east+min_east)/2, (max_north+min_north)/2)
    sea_level = API.getSeaLevel(center_point,
                                date=date)
    print(sea_level)
    p = Path(__file__).parent
    sosi_file_list = [p/"files_input"/folderName/"SOSI"/f for f in os.listdir(p/"files_input"/folderName/"SOSI") if f.endswith("Anlegg.SOS")]
    laz_file_list = [p/"files_input"/folderName/"LAZ"/f for f in os.listdir(p/"files_input"/folderName/"LAZ")]
    orto_photo = p/"files_input"/folderName/"ORTOPHOTO"/os.listdir(p/"files_input"/folderName/"ORTOPHOTO")[0]
    o_photo = ortophoto.of(orto_photo)
    o_photo.createCroppedPicture((maxOest,maxNord),(minOest,minNord),foldername=folderName)
    
    coast_mesh = mesh.mesh3d(filenameList=laz_file_list,
                             maxEast=max_east, minEast=min_east, maxNorth=max_north, minNorth=min_north,sl = sea_level)
    sosi = sosi_reader.SOSI(sosi_file_list[0], maxN=max_north, minN= min_north, maxO=max_east, minO=min_east)
    points_on_floaters = [int(sosi.calculatePointInsideBrygge(point)) for point in tqdm(coast_mesh.points[:,:2])]
    coast_mesh.points = np.array([[coast_mesh.points[i][0],coast_mesh.points[i][1], coast_mesh.points[i][2]+ points_on_floaters[i]*(sea_level-coast_mesh.sea_level_of_pc)] for i in tqdm(range(len(coast_mesh.points)))])
    coast_mesh.edgesort_mesh(lim = 3, sl = sea_level)
    coast_mesh.addSeaMesh_toPoints()
    gltf.CreategGLTF(coast_mesh.points, coast_mesh.edges, coast_mesh.sea_mesh, min_east, min_north,
                    Ndiff = (np.max(coast_mesh.points[:,1])- np.min(coast_mesh.points[:,1])),
                    Odiff = (np.max(coast_mesh.points[:,0])- np.min(coast_mesh.points[:,0])),
                    folderName= folderName, time = date.strftime("%m%d%Y%H:%M"),sl='{0:.{1}f}'.format(sea_level,3).replace("-","N"))






p = Path(__file__).parent
if __name__  == "__main__":
        
        folderName ="korsavika"#"Oslo" # eller "Ravnkloa"
        maxOest = 571490.68
        minOest = 571080.89
        maxNord = 7036625.1
        minNord = 7036148.91

    



        pyCoast(foldername=folderName,max_east=maxOest, min_east=minOest, max_north=maxNord, min_north=minNord, 
            date=datetime.datetime(year = 2024, month=12, day = 11,hour= 10, minute=20)) #Trondheim High Tide = 2024-07-11-14-30
