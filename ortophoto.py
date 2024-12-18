import rasterio 
import math
import numpy as np
from PIL import Image
from matplotlib import pyplot
from pathlib import Path

p = Path(__file__).parent
#foldername = "korsavika"#"Ravnkloa"#"Oslo"

class of:
    def __init__(self, filename) -> None:
        with rasterio.open(p / filename) as orto: 
            self.n_bands         =  orto.count
            self.rows, self.cols =  orto.shape
            self.transform       =  orto.transform
            self.projection         =  orto.crs
            self.data            =  orto.read()
            

        pass

    

    def createCroppedPicture(self, top, bottom,foldername):
        inv = ~self.transform
        pTx, pTy = inv*top
        pBx, pBy = inv*bottom 
        pTx = math.ceil(pTx-0.99)
        pTy = math.ceil(pTy-0.99)
        pBx = math.ceil(pBx-0.99)
        pBy = math.ceil(pBy-0.99)
        imgArr = self.data[:, pTy:pBy, pBx:pTx]
        
        H = np.array([imgArr[:,i,j] for i in range(len(imgArr[0])) for j in range(len(imgArr[0][0]))], dtype = 'uint8')
        
        a = np.arange(imgArr.shape[1]*imgArr.shape[2]).reshape(imgArr.shape[1:])
        img = Image.fromarray(H[a], 'RGB')
        img.save(p / 'files_output'/foldername/'cropped.png')
       
        





if __name__ == "__main__":
    
    

    src = rasterio.open(p/"files_input"/"Ravnkloa"/"ORTOPHOTO"/"Eksport-nib.tif")

    pyplot.imshow(src.read(1), cmap='pink')


    pyplot.show()   


        





