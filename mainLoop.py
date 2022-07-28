import cv2 as cv
import numpy as np

import time

import motors
import Pcontroller
import camera
import sys

'''
mode 0 = route image acquisition 
'''

if __name__=="__main__":
    mode=int(sys.argv[1])
    folder=sys.argv[2]
    print(mode)

    if mode==0:
        print(mode)
        while True:
            print(folder)
            filename=camera.record_frame(folder)
        #vicon.
