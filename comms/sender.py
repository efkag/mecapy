# credit https://github.com/ancabilloni/udp_camera_streaming

from __future__ import division
import cv2
import numpy as np
import socket
import struct
import math
import os
import sys

path = os.path.join(os.path.dirname(__file__), os.pardir)
fwd = os.path.dirname(__file__)
sys.path.append(path)

from camera import camera

class FrameSegment(object):
    """ 
    Object to break down image frame segment
    if the size of image exceed maximum datagram size 
    """
    MAX_DGRAM = 2**16
    MAX_IMAGE_DGRAM = MAX_DGRAM - 64 # extract 64 bytes in case UDP frame overflown
    def __init__(self, sock, port, addr):
        self.s = sock
        self.port = port
        self.addr = addr

    def udp_frame(self, img,transform, experimentState):
        """ 
        Compress image and Break down
        into data segments 
        """


        compress_img = cv2.imencode('.jpg', img)[1]
        transformbytes=np.array(transform).tobytes()

        dat =experimentState['live'].to_bytes(1,byteorder='big')+ experimentState['record'].to_bytes(1,byteorder='big')+experimentState['mode'].to_bytes(1,byteorder='big')+experimentState['recordTransform'].to_bytes(1,byteorder='big')+transformbytes+compress_img.tobytes()
        


        size = len(dat)
        count = math.ceil(size/(self.MAX_IMAGE_DGRAM))
        array_pos_start = 0
        while count:
            array_pos_end = min(size, array_pos_start + self.MAX_IMAGE_DGRAM)
            self.s.sendto(struct.pack("B", count) + dat[array_pos_start:array_pos_end], 
                (self.addr, self.port)
                )
            array_pos_start = array_pos_end
            count -= 1


def sendImage(s,fs,frame,transform,experimentState):
    frame=camera.processForSending(frame)
    #print(transform)
    fs.udp_frame(frame,transform,experimentState)
    if experimentState['mode']==2:

        try:
            seg,add=s.recvfrom(2**16)
            #print(seg)
            return(seg)
        except:
            seg=None
        #return(seg)
    else:
        return(None)

    #except:
        #pass


def createSocket(port=50001,addr="192.168.1.14"): #"192.168.1.89"
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)   
    s.setblocking(0)
    fs = FrameSegment(s, port,addr)
    return(s,fs)

