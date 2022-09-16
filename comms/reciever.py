#!/usr/bin/env python

# IMPORTANT: THIS SCRIPT IS FOR THE COMPUTER DOING THE CALCULATIONS

from __future__ import division
import cv2
import numpy as np
import socket
import struct
import os
import sys
import torch
import torchvision.transforms as transforms
from threading import Thread

from queue import Queue

from torchvision import datasets, transforms

from PIL import Image
import matplotlib.pyplot as plt
path = os.path.join(os.path.dirname(__file__), os.pardir)
fwd = os.path.dirname(__file__)
sys.path.append(path)
print(str(path))

import pickle

MAX_DGRAM = 2**16

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

hq=Queue()
hq.put(0)
imgQ=Queue()
rfsQ=Queue()


def test(img,no):
    # Your model testing code here
    return(heading,RFF)

def train():
    # Your model training code here
    return("Model Trained ")


def dump_buffer(s):
    """ Emptying buffer frame """
    while True:
        seg, addr = s.recvfrom(MAX_DGRAM)
        print(seg[0])
        if struct.unpack("B", seg[0:1])[0] == 1:
            print("finish emptying buffer")
            break

def main():
    """ Getting image udp frame &
    concate before decode and output image """

    # Set up socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("192.168.1.14", 50001)) # "192.168.1.14"
    dat = b''
    dump_buffer(s)

    i=0
    no=0

    plt.ion()
    while True:


        seg, addr = s.recvfrom(MAX_DGRAM)
        if struct.unpack("B", seg[0:1])[0] > 1:
            dat += seg[1:]
        else:
            dat += seg[1:]

            img = cv2.imdecode(np.fromstring(dat[3:], dtype=np.uint8), 1)

            if(dat[1])==0:

                cv2.imshow('frame', img)
                cv2.waitKey(1)

            else:
                print(no)
                no=no+1
                if no%2==0:
                    cv2.imshow('frame', img)
                    print("/Users/amany/Documents/ViewBasedNavigation/UnitySim/TrainImages/frameshot"+str(no)+'.png')
                    cv2.imwrite("/Users/amany/Documents/ViewBasedNavigation/UnitySim/TrainImages/frameshot"+str(no)+'.png',img)

            if dat[0]==0:
                if dat[2]==1:
                    train()
                    print('training!')
                    break

            # if dat[2]==1 # train
            # train("TrainImages")
            # if dat[2]==2 # test

            # Cant test as fast as frame rate- will cause massive delays
            # Only do the next calculation when the previous one is complete
            # Otherwise end up making movements for the past

            if dat[2]==2:
                if imgQ.empty():
                    imgQ.put(img)

                if hq.empty()==True:
                    #print('not empty')
                    continue
                else:
                    heading=hq.get(block=False)
                    heading=str(heading)
                    headingarr = bytes(heading, 'utf-8')
                    s.sendto(headingarr,addr)

                if rfsQ.empty()==False:
                    r=rfsQ.get(block=False)
                    plt.figure(2)
                    plt.clf()
                    plt.plot(r)
                else:
                    print('no rff')

            i=i+1

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            dat = b''

    print(dat[2])
    cv2.destroyAllWindows()
    s.close()


def WaitforHeading():
    no=0
    while True:
        if hq.empty()==True and imgQ.empty()==False:
            img=imgQ.get()
            no=no+1
            heading,r=test(img,no)
            #print('\n testing!',heading)
            r=r.squeeze().tolist()
            # heading has been calculated, put in the Q
            hq.put(heading)
            rfsQ.put(r)

            #print(headingarr)
            #print(addr[0])
            #print(headingarr.decode('utf-8'))



if __name__ == "__main__":

    calcThread=Thread(target=WaitforHeading)
    calcThread.daemon=True
    calcThread.start()
    main()



    #
    #train()

