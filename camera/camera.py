import cv2 as cv
import numpy as np

import time
import os

cam = cv.VideoCapture(0)
#

cam.set(3,360)
cam.set(4,360)


dir_path = os.path.dirname(os.path.realpath(__file__))

if cam.isOpened():
	print('Camera is open')
else:
	raise RuntimeError('Camera is off')

def read_frame():
	ret, frame = cam.read()
	return frame if ret else None


def record_frame(foldername,unwrapImage=True):
    frame = read_frame()
    if unwrapImage:
        frame=unwrap(frame)
    folder=os.path.join(dir_path,foldername)
    number_files=len(os.listdir(folder))
    
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    filename=foldername+'/test'+str(number_files+1)
    cv.imwrite(filename+'.png', frame)
    return(filename)

def unwrap(imgIn):
    
        
    #MAPPING
    def buildMap(Wd, Hd, R, Cx, Cy):
                    
        ys=np.arange(0,int(Hd))
        xs=np.arange(0,int(Wd))
        
        rs=np.zeros((len(xs),len(ys)))
        rs=R*ys/Hd
        
        thetas=np.expand_dims(((xs-offset)/Wd)*2*np.pi,1)

        map_x=np.transpose(Cx+(rs)*np.sin(thetas)).astype(np.float32)
        map_y=np.transpose(Cy+(rs)*np.cos(thetas)).astype(np.float32)
        return map_x, map_y

    #UNWARP
    def unwarp(img, xmap, ymap):
        output = cv.remap(img, xmap, ymap, cv.INTER_LINEAR)
        return output
    
    
    img = imgIn
    
    cropBlock=int((int(img.shape[1])-int(img.shape[0]))/2)
    img=img[:,cropBlock:-cropBlock]

    #distance to the centre of the image
    offset=int(img.shape[0]/2)

    #IMAGE CENTER
    Cx = img.shape[0]/2
    Cy = img.shape[1]/2

    #RADIUS OUTER
    R =- Cx

    #DESTINATION IMAGE SIZE
    Wd = int(abs(2.0 * (R / 2) * np.pi))
    Hd = int(abs(R))

    #BUILD MAP
    xmap, ymap = buildMap(Wd, Hd, R, Cx, Cy)

    #UNWARP
    result = unwarp(img, xmap, ymap)

    return result

record_frame('images',unwrapImage=True)
