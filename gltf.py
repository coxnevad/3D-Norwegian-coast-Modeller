import pygltflib
import numpy as np
from pathlib import Path
import pygltflib.utils

p = Path(__file__).parent



R_GLTF3D = np.array([[-1,0,0],
                   [0,0,1],
                   [0,1,0]], dtype = 'float32')

def CreategGLTF(points, terrain,sea,minO,minN,Ndiff, Odiff,folderName,time,sl):
    points = np.add(points,np.array([-minO, -minN, 0]), dtype= 'float64')
    points_mesh = np.matmul(np.array(points, dtype='float64'),R_GLTF3D, dtype= 'float32')
    terrain = terrain.astype('uint32')
    sea = sea.astype('uint32')
    

    divisor = np.array([Odiff, -Ndiff, 1], dtype='float32')
    imgPoints   = np.transpose(np.transpose(points)/divisor[:,None]).astype('float32')


    imgPoints = np.add(imgPoints, np.array(  [0,1,0], dtype='float32'), dtype='float32')
    imgPoints = imgPoints[:,:2]




    sea_binary_blob = sea.flatten().tobytes()
    terrain_binary_blob = terrain.flatten().tobytes()
    points_binary_blob = points_mesh.tobytes()
    imgPoints_blob = imgPoints.tobytes()


    gltf = pygltflib.GLTF2(
        scene=0,
        scenes=[pygltflib.Scene(nodes=[0,1])],
        nodes=[pygltflib.Node(mesh=0), pygltflib.Node(mesh=1)],
        meshes=[
            pygltflib.Mesh(
                primitives=[
                    pygltflib.Primitive(
                        attributes=pygltflib.Attributes(POSITION=1, TEXCOORD_0=2), indices=0,material=0
                    )
                ]
            ),pygltflib.Mesh(
                primitives=[
                    pygltflib.Primitive(
                        attributes=pygltflib.Attributes(POSITION=1),indices = 3, material = 1
                    )
                ]
            )
        ],
        textures=[
            pygltflib.Texture(
                sampler=0,
                source=0
            )

        ],
        materials=[
            pygltflib.Material(
                doubleSided=True,
                alphaMode=pygltflib.MASK,
                alphaCutoff=0.5,
                pbrMetallicRoughness=pygltflib.PbrMetallicRoughness(baseColorTexture=pygltflib.TextureInfo(index=0),
                                                                    metallicFactor=0.0,
                                                                    roughnessFactor=1.0)
            ),
            pygltflib.Material(
                doubleSided=True,
                alphaMode=pygltflib.MASK,
                alphaCutoff = 0.5,
                pbrMetallicRoughness = pygltflib.PbrMetallicRoughness(baseColorFactor=[0.011764705882352941,
                                                                                    0.011764705882352941,
                                                                                    1.0,
                                                                                    1])

            )
        ],
        samplers=[
            pygltflib.Sampler(magFilter=9729,
                            minFilter=9987,
                            wrapS=33648,
                            wrapT=33648
                            )
        ],
        accessors=[
            pygltflib.Accessor(
                bufferView=0,
                componentType=pygltflib.UNSIGNED_INT,
                count=terrain.size,
                type=pygltflib.SCALAR,
                max=[int(terrain.max())],
                min=[int(terrain.min())]
            ),
            pygltflib.Accessor(
                bufferView=1,
                componentType=pygltflib.FLOAT,
                byteOffset = 0,
                count=len(points_mesh),
                type=pygltflib.VEC3,
                max=points_mesh.max(axis=0).tolist(),
                min=points_mesh.min(axis=0).tolist(),
                    ),
            pygltflib.Accessor(
                bufferView=2,
                byteOffset=0,
                componentType=pygltflib.FLOAT,
                count=len(imgPoints),
                type=pygltflib.VEC2,
                max = imgPoints.max(axis=0).tolist(),
                min = imgPoints.min(axis=0).tolist()
                

            ),
            pygltflib.Accessor(
                bufferView=3,
                byteOffset=0,
                componentType=pygltflib.UNSIGNED_INT,
                count = sea.size,
                type = pygltflib.SCALAR,
                max = [int(sea.max())],
                min = [int(sea.min())]


            )
        ],
        bufferViews=[
            pygltflib.BufferView(
                buffer=0,
                byteLength=len(terrain_binary_blob),
                target=pygltflib.ELEMENT_ARRAY_BUFFER,
            ),
            pygltflib.BufferView(
                buffer=0,
                byteOffset=len(terrain_binary_blob),
                byteLength=len(points_binary_blob),
                target=pygltflib.ARRAY_BUFFER,
            ),


            pygltflib.BufferView(
                buffer = 0,
                byteOffset=len(terrain_binary_blob)+len(points_binary_blob),
                byteLength=len(imgPoints_blob),
                target = pygltflib.ARRAY_BUFFER,
            ),
            pygltflib.BufferView(
                buffer = 0,
                byteOffset = len(terrain_binary_blob)+len(points_binary_blob)+len(imgPoints_blob),
                byteLength=len(sea_binary_blob),
                target= pygltflib.ELEMENT_ARRAY_BUFFER,
                
            ),
        ],
        buffers=[
            pygltflib.Buffer(
                byteLength=len(terrain_binary_blob) + len(points_binary_blob)+len(imgPoints_blob)+len(sea_binary_blob)#+len(image_blob)
            )
        ],
    )
    
    

    gltf.set_binary_blob(terrain_binary_blob + points_binary_blob+imgPoints_blob+sea_binary_blob)
    glb = b"".join(gltf.save_to_bytes())
    gltf2 = pygltflib.GLTF2.load_from_bytes(glb)
    img = pygltflib.utils.Image()
    img.uri =str(p/"files_output"/folderName/"cropped.png")
    gltf2.images.append(img)
    gltf2.convert_images(pygltflib.utils.ImageFormat.DATAURI)
    fileName = f'{minO}&{minN}&{sl}.glb'
    gltf2.save(str(p/ "files_output"/folderName / fileName))
