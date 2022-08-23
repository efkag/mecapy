from ast import While
from platform import release
from socket import socket
from threading import Thread
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

    pressQueue = Queue()
    releaseQueue=Queue()
    killQueue=Queue()

    def write_keys(key,q):
        k = str(key).replace(f'{chr(39)}', '')
        q.put(k)

    def on_press(key):
        print('pressed')
        write_keys(key,pressQueue)

    def on_release(key):
        print('released')
        write_keys(key,releaseQueue)

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
            pass
        
        return(res)

    def mainloop():
        sendSocket,frameHolder=sender.createSocket()
        captureShot=0

        movementState={'throttle':int(3000/2),'live':1}
        modes=['manual','train','test']
        experimentState={'live':1,'mode':modes.index(mode),'record':0}

        while True:
            keysDown=tryq(pressQueue)
            if len(list(keysDown))!=0:
                captureShot=checkCaptureShotCondition(captureShot,keysDown)
                movementState=keyboard.action(keysDown,movementState)

            if movementState['live']==0:
                # send one final image with the death signal
                experimentState['live']=0
                sender.sendImage(sendSocket,frameHolder,frame,experimentState)
                killQueue.put(1)

            frame=camera.read_frame()
            #frame=np.random.rand(100,20)*255

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

        while True:
            events = inputs.get_key()
            for event in events:
                #print(event.ev_type, event.code, event.state)
                if event.ev_type=='Key':
                    if event.state!=0:
                        keysDown.add(event.code)
                    else:
                        if event.code in keysDown:
                            keysDown.remove(event.code)

                pressQueue.put(keysDown)

    keyinputThread=Thread(target=keyinputLoop)
    keyinputThread.daemon=True
    keyinputThread.start()

    main_thread=Thread(target=mainloop)
    main_thread.daemon=True
    main_thread.start()
    
    while True:
        try:
            k=killQueue.get()
        except:
            k=0
            pass
            
        if k==1:
            sys.exit()


    # Start threads - input libraries are often blocking
    #keyboardThread= keyboard.Listener(on_press=on_press,on_release=on_release)
    #keyboardThread.daemon=True
    #keyboardThread.start()