# 3D-Norwegian-coast-Modeller (pyCOast?)


###Code needs to be cleaned up###


#Structure
Within the same folders as the files, add a folder named "files_input" and "files_output". 
Within each folder, create the name of the project that is to be mapped. That is, two folders, one in input and one in output. 


within input folder create folders named "ORTOPHOTO", "SOSI" and "LAZ". THese are where the input data goes. TIde data is through teh web based API.
Within the output folder: create folder called "VIDEO"

From "pyCoast_main" enter coordinates, date and folder name to run. Make sure the data is in the same coordinate system (UTM)

To render Images, use Display Of Positions. Renders a produced glb file and recreats an example position of the given ooordinates within said gltf file. 
NOTE. Files need to keep their georeferencing. Two first numbers of produced glb files. 
