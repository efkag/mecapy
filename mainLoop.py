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
from MovementControl import joystickcontrols


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
    inputDevice='joystick'

    keydownQ = Queue()
    killQ=Queue()
    frameQ=Queue()
    movementStateQ=Queue()

    def checkCaptureShotCondition(captureShot,keysDown):
        if inputDevice=='keyboard':
            code='KEY_C'
        else:
            code='BTN_EAST'
        present=[1 if e[0]==code else 0 for e in list(keysDown)]
        if sum(present)!=0:
            captureShot=captureShot+1
            print(captureShot)

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


        #time=0main_thread
        while True:
            #z=timeit()
            #time=(time+z)/2
            #print(time)
            if inputDevice=='keyboard':
                newkeysDown=tryq(keydownQ)
                if 'n' in newkeysDown:
                    keysDown=keysDown
                else:
                    keysDown=newkeysDown
                
            else:
                try:
                    keysDown=keydownQ.get(block=False)
                except:
                    keysDown=set()
                    pass
                    
            
            if len(list(keysDown))!=0:
                print(keysDown)
                captureShot=checkCaptureShotCondition(captureShot,keysDown)
                if inputDevice=='keyboard':
                    movementState=keyboard.action(keysDown,movementState)
                if inputDevice=='joystick':
                    movementState=joystickcontrols.action(keysDown,movementState)
                    
            


            if frameQ.empty()==False:
                frame=frameQ.get(block=False)
                

                if movementState['live']==0:
                    # send one final image with the death signal
                    experimentState['live']=0
                    sender.sendImage(sendSocket,frameHolder,frame,experimentState)
                    print('killing')
                    killQ.put(1)

                if (mode=='manual' and captureShot==1) or (mode=='train'):
                    # stream and save image
                    experimentState['record']=1
                    
                    sender.sendImage(sendSocket,frameHolder,frame,experimentState)
                    
                else:
                    # just stream the images
                    experimentState['record']=0
                    sender.sendImage(sendSocket,frameHolder,frame,experimentState)


    mode=sys.argv[1]
    #folder=sys.argv[2]

    def keyinputLoop():
        keysDown={}
        keysDown=set()
        
        keydownQ.put(keysDown)
        
        if inputDevice=='keyboard':
            print(inputs.devices.keyboards) 
            keyboardIdx=1
        
        if inputDevice=='joystick':
            print(inputs.devices.gamepads)
            gamepadidx=1

        while True:
            try:
                # note: this needsyss you to change the input library to pick the keyboard based on an index
                # atm the library only selects the first keyboard device, problem if multiple keyboards connected
                if inputDevice=='keyboard':
                    events = inputs.get_key(keyboardIdx=keyboardIdx)
                else:
                    events = inputs.get_gamepad(gamepadidx=gamepadidx)
            except:
                if inputDevice=='keyboard':
                    events=inputs.get_key()
                else:
                    events=inputs.get_gamepad()
            #print(event.ev_type,event.code,event.state)
            
            
            for event in events:
                #print(event.ev_type, event.code, event.state)
                if event.ev_type=='Key' or event.ev_type=='Absolute':
                    
                    if inputDevice=='joystick':
                        keysDown=set()
                        keysDown.add((event.code,event.state))
                        
                        
                    if inputDevice=='keyboard':
                        
                        if event.state!=0:
                            #present=[1 if e[0]==event.code else 0 for e in list(keysDown)]
                            #if sum(present)!=0:
                                #[print(e) for e in list(keysDown) if e[0]==event.code]
                                #[keysDown.remove(e) for e in list(keysDown) if e[0]==event.code]
                                
                            if len(list(keysDown))==0:
                                keysDown.add((event.code,event.state))
                            
                            else:
                                for e in list(keysDown):
                                    if e[0]==event.code:
                                        print('r')
                                        keysDown.remove(e)
                                        keysDown.add((event.code,event.state))
                                        #print(keysDown)
                            
                            #print(keysDown)
                        else:
                            
                            
                            for e in list(keysDown):
                                if e[0]==event.code:
                                    print('r')
                                    keysDown.remove(e)
                                    #print(keysDown)
                            #[keysDown.remove(e) for e in list(keysDown) if e[0]==event.code]
                            #print(keysDown)
                        
                        
            #print(keysDown)            
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

