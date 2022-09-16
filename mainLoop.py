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
from motors import Pcontroller
from motors import motors


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
        kd=(keysDown.copy())
        pkd=(priorKeysDown.copy())


         ### THIS WILL WAIT FOR RELEASE
        if inputDevice=='joystick':
            code='BTN_EAST'
            
            # initial conditions (key has not yet been pressed and released)
            if code in kd and (code not in pkd):
                if kd[code]!=0:
                    captureShot=1
                else:
                    captureShot=0
            else:
                if (code in kd) and (code in pkd):
                    if kd[code]!=pkd[code]:
                        if kd[code]!=0 and pkd[code]==0: 
                            captureShot=1
                        # if it hasnt been caught on the way down, catch on the way up
                        elif captureShot==0 and kd[code]==0 and pkd[code]==1:
                            captureShot=1
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
        Pcontroller_=Pcontroller.deg2gain()

        
        modes=['manual','train','test']
        experimentState={'live':1,'mode':modes.index(mode),'record':0}
        
        movementState={'throttle':int(3000/2),'live':1}
        localCaptureShot=0;
        priorKeysDown={}
        keysDown={}
        prevtime=0
        h=0
        #time=0main_thread
        while True:
            #z=timeit()
            #time=(time+z)/2
            #print(time)
            

            try:
                nkd=keydownQ.get(block=False)
                
                keysDown=nkd
                
            except:
                pass

                

            captureShot=checkCaptureShotCondition(captureShot,keysDown,priorKeysDown)
            priorKeysDown=keysDown.copy()

            if inputDevice=='joystick':
                movementState=joystickcontrols.action(keysDown,movementState)
            
                


            if frameQ.empty()==False:
                frame=frameQ.get(block=False)


                if movementState['live']==0:
                    # send one final image with the death signal
                    if experimentState['live']!=0:
                        print('killing')
                        experimentState['live']=0
                    sender.sendImage(sendSocket,frameHolder,frame,experimentState)
                    killQ.put(1)

                elif (mode=='manual' and captureShot>=1) or (mode=='train'):
                    # stream and save image
                    experimentState['record']=1
                    
                    sender.sendImage(sendSocket,frameHolder,frame,experimentState)
                    captureShot=-1
                    print('save, reset capture shot',captureShot)
                    
                elif (mode=='test'):
                    #print(experimentState['mode'])
                    
                    
                    heading=sender.sendImage(sendSocket,frameHolder,frame,experimentState)
                    #print(heading)

                    if heading!=None:
                        h=int(heading.decode("utf-8"))
                        gain=Pcontroller_.convert(h)
                        newtime=time.time()
                        
  
                        drive=1
                        
                        prevtime=newtime
                        
                        forwardgain=80
                        #print('fg',forwardgain)
                        #print('tg',gain)
                        fg=forwardgain-gain
                        #print(fg)
                        if fg<gain:
                            fg=gain
                        #print(fg)
                        if abs(h)>10:
                            
                            print('Rotating on the spot')
                            
                            if h<0:
                                motors.right([gain]*4)
                                #print('B turning left')
                            if h>0:
                                #print('B turning right')
                                motors.left([gain]*4)
                                
                        else:
                            if h<0:
                                print('G turning l')
                                motors.drive([1,1,1,1],[60+gain,60,60+gain,60])
                            if h>0:
                                print('G turning r')
                                motors.drive([1,1,1,1],[60,60+gain,60,60+gain])
                            if h==0:
                                print('forward')
                                motors.drive([drive,drive,drive,drive],[forwardgain,forwardgain,forwardgain,forwardgain])
                            
                                
                                
                                

    
                else:
                    # just stream the images
                    experimentState['record']=0
                    sender.sendImage(sendSocket,frameHolder,frame,experimentState)
                
                

                    
                

                


    mode=sys.argv[1]
    #folder=sys.argv[2]

    def keyinputLoop():
        keysDown={}
        keydownQ.put(keysDown)

        
        if inputDevice=='joystick':
            print(inputs.devices.gamepads)
            gamepadidx=1

        while True:
            try:
                events = inputs.get_gamepad(gamepadidx=gamepadidx)
            except:
                events=inputs.get_gamepad()
            #print(event.ev_type,event.code,event.state)
            
            
            for event in events:
                #print(event.ev_type, event.code, event.state)
                if event.ev_type=='Key' or event.ev_type=='Absolute':
                    
                    if inputDevice=='joystick':
                        keysDown[event.code]=event.state

                        
            
            #print(keysDown)            
            keydownQ.put(keysDown)


    def getCameraFrames():
        while True:
            frame=camera.read_frame()
            #frame=np.random.rand(100,20)*255
            frameQ.put(frame)
            
    def getTransform():
        transformQ.put(transform)

    def startThread(threadTarget):
        thread=Thread(target=threadTarget)
        thread.daemon=True
        thread.start()
        return(thread)

    keyinputThread=startThread(keyinputLoop)
    cameraThread=startThread(getCameraFrames)
    viconThread=startThread(getTransform)

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
