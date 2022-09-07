import socket
import struct
#UDP_IP = '192.168.1.9'
UDP_IP = '192.168.1.7'
UDP_IP = ''
UDP_PORT = 51001


soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

soc.bind((UDP_IP, UDP_PORT))

while True:
    data, addr = soc.recvfrom(1024)
    print(addr)
    #data = list(data)
    #print(''.join(chr(i) for i in data))
    #print(list(data))
    print(struct.unpack('!f', data))
