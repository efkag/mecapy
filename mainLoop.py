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
from motors import Pcontroller, motors
from vicon import vicon


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
    transformQ=Queue()

    def checkCaptureShotCondition(captureShot,keysDown,priorKeysDown):
        kl=list(keysDown.copy())
        priorkl=list(priorKeysDown.copy())


         ### THIS WILL WAIT FOR RELEASE
        if inputDevice=='joystick':
            code='BTN_EAST'

            e=[e for e in kl if e[0]==code]
            pe=[e for e in priorkl if e[0]==code]


            if len(pe)!=0 and len(e)!=0:

                if pe[0][1]<e[0][1]:
                    print('pressed')
                    captureShot=1


            # initial conditions?
            if len(pe)==0 and len(e)!=0:
                if captureShot==0:
                    captureShot=captureShot+1
                    print('code present',captureShot)
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
        Pcontroller_=Pcontroller.deg2gain()


        modes=['manual','train','test']
        experimentState={'live':1,'mode':modes.index(mode),'record':0}

        movementState={'throttle':int(3000/2),'live':1}
        localCaptureShot=0;
        priorKeysDown=set()
        prevtime=0
        h=0

        while True:

            try:
                keysDown=keydownQ.get(block=False)
            except:
                keysDown=set()
                pass


            if len(list(keysDown))!=0:

                captureShot=checkCaptureShotCondition(captureShot,keysDown,priorKeysDown)

                if inputDevice=='joystick':
                    movementState=joystickcontrols.action(keysDown,movementState)
                priorKeysDown=keysDown


            if frameQ.empty()==False:
                frame=frameQ.get(block=False)
                transform=transformQ.get(block=False)

                if movementState['live']==0:
                    # send one final image with the death signal
                    experimentState['live']=0
                    sender.sendImage(sendSocket,frameHolder,frame,transform,experimentState)

                    print('killing')
                    killQ.put(1)

                elif (mode=='manual' and captureShot>=1) or (mode=='train'):
                    # stream and save image
                    experimentState['record']=1

                    sender.sendImage(sendSocket,frameHolder,frame,transform,experimentState)
                    captureShot=0
                    print('save, reset capture shot',captureShot)

                elif (mode=='test'):
                    heading=sender.sendImage(sendSocket,frameHolder,frame,transform,experimentState)
                    print(heading)

                    if heading!=None:
                        h=int(heading.decode("utf-8"))
                        gain=Pcontroller_.convert(h)
                        #newtime=time.time()

                        if h<0:
                            motors.right([gain]*4)
                        if h>0:
                            motors.left([gain]*4)

                        if abs(h)<=6:
                            motors.forward([80]*4)

                else:
                    # just stream the images
                    experimentState['record']=0
                    sender.sendImage(sendSocket,frameHolder,frame,transform,experimentState)


    mode=sys.argv[1]
    #folder=sys.argv[2]

    def keyinputLoop():
        keysDown={}
        keysDown=set()

        keydownQ.put(keysDown)

        if inputDevice=='joystick':
            print(inputs.devices.gamepads)
            gamepadidx=1

        while True:
            try:
                # note: this needs you to change the input library to pick the keyboard based on an index
                # atm the library only selects the first keyboard device, problem if multiple keyboards connected
                events = inputs.get_gamepad(gamepadidx=gamepadidx)
            except:
                events=inputs.get_gamepad()

            for event in events:
                #print(event.ev_type, event.code, event.state)
                if event.ev_type=='Key' or event.ev_type=='Absolute':

                    if inputDevice=='joystick':
                        keysDown=set() # gets reset every time
                        keysDown.add((event.code,event.state))

            keydownQ.put(keysDown)


    def getCameraFrames():
        while True:
            frame=camera.read_frame()
            #frame=np.random.rand(100,20)*255
            frameQ.put(frame)

    def getViconTransform():
        vicsoc=vicon.CreateSocket()
        while True:
            transform=vicon.ReadTransform(vicsoc)
            if len(transform)!=0:
                transformQ.put(transform)

    def startThread(threadTarget):
        thread=Thread(target=threadTarget)
        thread.daemon=True
        thread.start()
        return(thread)

    keyinputThread=startThread(keyinputLoop)
    cameraThread=startThread(getCameraFrames)
    viconThread=startThread(getViconTransform)

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
            motors.stop()
            time.sleep(2)
            sys.exit()
