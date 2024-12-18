import trimesh
import os
import pyrender
import cv2
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

p = Path(__file__).parent

R_GLTF3D = np.matrix([[-1,0,0],
                   [0,0,1],
                   [0,1,0]], dtype = 'float32')

#From xyz = ENH to gltf standard


R_NED = np.matrix([[0,1,0],
                   [1,0,0],
                   [0,0,-1]
                   
                   ])

#from xyz to NED

R_CMERA2X_AXIS = np.matrix([[0,1,0],
                            [0,0,-1],
                            [-1,0,0]]).T

# From camera to NED


def rotateZ(t):
    r = np.matrix([
    [np.cos(t),-np.sin(t) , 0],
    [np.sin(t), np.cos(t), 0],
    [0.0,  0.0,   1.0]])
    return r


def rotateX(t):
    r= np.matrix([
        [1,0,0],
        [0,np.cos(t),-np.sin(t)],
        [0,np.sin(t),np.cos(t)]

        ])
    return r

def rotateY(t):
    r = np.matrix([[np.cos(t),0,np.sin(t)],
            [0,1,0],
             [-np.sin(t),0,np.cos(t)]
            
             
             ])
    return r


def CreatePose(R, T):
    return np.concatenate((np.concatenate((R,T), axis = 1),np.array([[0,0,0,1]])), axis = 0)







#projectFolder  = filename[:-4].split("&")[2]
def createTrajectory(point, baseE,baseN):
    steps = np.linspace(0,27,400)
    l = list()
    for s in steps:
        pt = point + 0*s*np.array([0.1,0,0]) 
        rll = 0.43+s*np.pi/25*-1
        l.append(createPose(pt, pitch= -0.15, yaw = rll, roll = 0, baseE=baseE,baseN=baseN))


    return l




def createPose(point,roll=0,pitch=0,yaw = 0, baseE=0,baseN=0):
    #xyz_roll_pitch_yaw
    t = np.transpose(np.matmul(point-np.array([baseE, baseN, 0]),R_GLTF3D))
    r =R_GLTF3D.T*R_NED.T*rotateZ(yaw)*rotateY(pitch)*rotateX(roll)*R_CMERA2X_AXIS
        #To gltf from XYZ, to xyz_from NED, Rotation in NED, ned from CameraRotation MAtrix




    return CreatePose(r,t)



    
   

def take_imgs_ex(projectfolder, filename,video_list= None): #series of coordinates, and angle
    ren = pyrender.OffscreenRenderer(800,800)
    
    
    coast_gltf = trimesh.load(p/  "files_output"/projectFolder/ filename , file_type="glb")
    coastMesh = pyrender.Mesh.from_trimesh(list(coast_gltf.geometry.values())[0])
    oceanMesh = pyrender.Mesh.from_trimesh(list(coast_gltf.geometry.values())[1])
    a = list(coast_gltf.geometry.values())
    sl = a[0].vertices[a[1].faces[0][0]][1]


    
    scene = pyrender.Scene(ambient_light=np.array([1.0, 1.0, 1.0, 1.0]))

    scene.add(coastMesh)
    scene.add(oceanMesh)
    c = 1

    for e in video_list:
        
        
        stamp = '{0:0>3}'.format(c)


        
        cam = pyrender.PerspectiveCamera(yfov=(np.pi / 3.0))


        cam_pose = e


        cam_node = scene.add(cam, pose=np.array(cam_pose))
        color, depth = ren.render(scene)
        im = Image.fromarray(color)
        tag = filename+"_"+stamp+".png"
        im.save(p/"files_output"/projectFolder/"VIDEO"/tag)
        scene.remove_node(cam_node)
        c+=1
    video_name = "TST.avi"
    img_folder = p/"files_output"/projectFolder/"VIDEO"
    images = [img for img in os.listdir(img_folder)]
    frame = cv2.imread(os.path.join(img_folder, images[0]))
    height, width, layers = frame.shape   
    video = cv2.VideoWriter(p/"files_output"/projectFolder/video_name, 0, 30, (width, height))
    for image in images:  
        video.write(cv2.imread(os.path.join(img_folder, image)))  
    cv2.destroyAllWindows()  
    video.release()
    

def main_display(folder, filename, north, east, moh):
    baseE = float(filename[:-4].split("&")[0])
    baseN = float(filename[:-4].split("&")[1])


    test_center_point= np.array([east,north,moh])
    points = createTrajectory(test_center_point,baseE=baseE,baseN=baseN) #simulating a set of points with poses. 
    take_imgs_ex(video_list=points,projectfolder=folder,filename=filename)





if __name__ == "__main__":

    
    projectFolder = "Ravnkloa"

    filename = "569427.7&7034657.87&0.181Ravnkloa.glb"

    #position in corresponding UTM (32)

    N = 7034704.77
    E = 569507.57
    h = 3.7

    main_display(folder = projectFolder,filename=filename, north=N, east=E,moh = h)
    



        