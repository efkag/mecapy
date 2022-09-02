import cv2 as cv
import numpy as np

import time
import os

cam = cv.VideoCapture(0)
#
# must be one of the specified resolutions of the pixpro - see tech specs
# picked lowest that was still spherical (1072x1072 was not)
cam.set(3,1440)
cam.set(4,1440)
#cam.set(5,30)


for i in range(0,10):
    print('arg',i)
    print(cam.get(i))


dir_path = os.path.dirname(os.path.realpath(__file__))

if cam.isOpened():
	print('Camera is open')
    
else:
	raise RuntimeError('Camera is off')

def read_frame():
    ret, frame = cam.read()
    return frame if ret else None

def processForSending(frame):
    frame=cv.cvtColor(frame,cv.COLOR_BGR2GRAY)
    frame=unwrap(frame)
    #frame=cv.cvtColor(frame,cv.COLOR_BGR2GRAY)
    frame=cv.resize(frame,(120,25))
    return(frame)

def record_frame(foldername,saveOriginal=False):
    frame = read_frame()
    if saveOriginal==False:
        frame = processForSending(frame)
    folder=os.path.join(dir_path,foldername)
    
    if not os.path.exists(folder):
        os.makedirs(folder)

    number_files=len(os.listdir(folder))
    filename=folder+'\\test'+str(number_files+1)+'.png'
    cv.imwrite(filename, frame)
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
    def unwarp(_img, xmap, ymap):
        
        output = cv.remap(_img, xmap, ymap, cv.INTER_LINEAR)
        return output
    

    img=cv.resize(imgIn,None,fx=0.1,fy=0.1,interpolation=cv.INTER_LINEAR)

    #img = imgIn

    if img.shape[1] != img.shape[0]:
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
'''

start=time.time()
running=0


while True:
    frame=read_frame()
    frame=processForSending(frame)
    cv.imshow("frame",frame)
    cv.waitKey(1)
    current=time.time()
    dif=current-start
    start=current
    running+=dif
    running=running/2
    #print(running)
'''