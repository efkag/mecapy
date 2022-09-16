import socket
import struct
import sys
from unittest.util import unorderable_list_difference
import numpy as np

UDP_IP = ''
UDP_PORT = 51001

"""
The binary string from the VICON is as follows:

4 byte unsigned - frame number
1 byte unsigned - number of objects

That's followed by that many objects, each of which consist of:

1 byte - unused x
2 byte unsigned - object size (should always be 72)
24 bytes - string containing object name
8 byte double - x
8 byte double - y
8 byte double - z
8 byte double  - yaw
8 byte double - pitch
8 byte double - roll

"""



#print(sys.byteorder)

def CreateSocket():

    soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    soc.setblocking(0)
    soc.bind((UDP_IP, UDP_PORT))
    print('bound')

    return(soc)

def UnpackTransform(data):

    # TODO future proof for other boards
    headerfmt='<LB'
    restfmt='<xH24s6d'


    size = struct.calcsize(restfmt)
    headersize=struct.calcsize(headerfmt)
    res=struct.unpack(headerfmt, data[:headersize])

    for i in range(0,res[1]):
        res=struct.unpack(restfmt,data[headersize+i*(size):headersize+size+i*(size)])

    transform=res[-6:]
    #print(transform)
    return(transform)

    #return struct.unpack(fmt, data[6:6+size])


def ReadTransform(vicsoc):
    try:
        data,addr=vicsoc.recvfrom(1024)
        transform=UnpackTransform(data)
        transform=np.array(transform)

    except:
        transform=None

    return(transform)

"""
soc=CreateSocket()
while True:

    data, addr = soc.recvfrom(1024)
    print(data)
    print(UnpackTransform(data))
"""