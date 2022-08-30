from ast import While
from platform import release
from shutil import move
from socket import socket
from threading import Thread
from timeit import timeit
from tracemalloc import start
from typing import Tuple
import cv2 as cv
import numpy as np
import inputs

import time

import motors
#import Pcontroller
from camera import camera
import os
import sys
from comms import sender
import time

from queue import Queue

from MovementControl import keyboard


#from MovementControl import keyboardcontrols
'''
mode 0 = manual
    Press 'c' to capture images
mode 1 = training (will acquire images and train a model on them )
mode 2 = testing
'''

# replace try/ exceptions with just checking if the queue is empty in places

if __name__=="__main__":
    user_input='n'

    keydownQ = Queue()
    killQ=Queue()
    frameQ=Queue()
    movementStateQ=Queue()

    def checkCaptureShotCondition(captureShot,keysDown):
        if 'KEY_C' in keysDown:
            captureShot=captureShot+1
        else:
            captureShot=0
        return(captureShot)

    def tryq(q):
        try:
            res=q.get(block=False)
        except:
            res=set()
            res.add('n')
            pass
        return(res)

    def mainloop():
        sendSocket,frameHolder=sender.createSocket()
        captureShot=0

        
        modes=['manual','train','test']
        experimentState={'live':1,'mode':modes.index(mode),'record':0}
        movementState={'throttle':int(3000/2),'live':1}

        #time=0
        while True:
            #z=timeit()
            #time=(time+z)/2
            #print(time)
            newkeysDown=tryq(keydownQ)
            if 'n' in newkeysDown:
                keysDown=keysDown
            else:
                keysDown=newkeysDown
            
            #print(keysDown)

            if len(list(keysDown))!=0:
                captureShot=checkCaptureShotCondition(captureShot,keysDown)
                movementState=keyboard.action(keysDown,movementState)

                

            if frameQ.empty()==False:
                frame=frameQ.get(block=False)
                

                if movementState['live']==0:
                    # send one final image with the death signal
                    experimentState['live']=0
                    #sender.sendImage(sendSocket,frameHolder,frame,experimentState)
                    killQ.put(1)

                if (mode=='manual' and captureShot==1) or (mode=='train'):
                    # stream and save image
                    experimentState['record']=1
                    #sender.sendImage(sendSocket,frameHolder,frame,experimentState)
                    
                else:
                    # just stream the images
                    experimentState['record']=0
                    #sender.sendImage(sendSocket,frameHolder,frame,experimentState)


    mode=sys.argv[1]
    #folder=sys.argv[2]

    def keyinputLoop():
        keysDown={}
        keysDown=set()
        
        keydownQ.put(keysDown)

        print(inputs.devices.keyboards) 
        keyboardIdx=1

        while True:
            events = inputs.get_key(keyboardIdx=keyboardIdx)

            #print(event.ev_type,event.code,event.state)
            for event in events:
                #print(event.ev_type, event.code, event.state)
                if event.ev_type=='Key':
                    
                    if event.state!=0:
                        keysDown.add(event.code)
                    else:
                        if event.code in keysDown:
                            keysDown.remove(event.code)
                            events=inputs.get_key()
            keydownQ.put(keysDown)

    def getCameraFrames():
        while True:
            frame=camera.read_frame()
            #frame=np.random.rand(100,20)*255
            frameQ.put(frame)

    def startThread(threadTarget):
        thread=Thread(target=threadTarget)
        thread.daemon=True
        thread.start()
        return(thread)

    keyinputThread=startThread(keyinputLoop)
    cameraThread=startThread(getCameraFrames)

    main_thread=Thread(target=mainloop)
    main_thread.daemon=True
    main_thread.start()
    
    while True:
        try:
            k=killQ.get()
        except:
            k=0
            pass
            
        if k==1:
            sys.exit()

