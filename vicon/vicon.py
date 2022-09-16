import socket
import struct
import sys
from unittest.util import unorderable_list_difference

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
print(sys.byteorder)

def CreateSocket():

    soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        soc.bind((UDP_IP, UDP_PORT))
        print('bound')
    except socket.error as e:
        print(e)
    return(soc)


def UnpackTransform(data):

    headerfmt='<LB'
    restfmt='<xH24s6d'

    headerfmt='=B'
    restfmt='=xH24s6d'

    size = struct.calcsize(restfmt)
    headersize=struct.calcsize(headerfmt)
    res=struct.unpack(headerfmt, data[:headersize])

    for i in range(0,res[1]):
        res=struct.unpack(restfmt,data[headersize+i*(size):headersize+size+i*(size)])
        print(res)

    transform=res[-6:]
    return(transform)

def ReadTransform(vicsoc):
    try:
        data, addr = vicsoc.recvfrom(1024)
        transform=UnpackTransform(data)
    except:
        transform=[]
    return(transform)

