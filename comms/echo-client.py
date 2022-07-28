# echo-client.py

import socket
import cv2 as cv

HOST = "192.168.1.14"  # The server's hostname or IP address
PORT = 50000  # The port used by the server


    
filename='images/test1'
image=cv.imread(filename+'.png')
image=cv.resize(image,(120,25))
grayImage=cv.cvtColor(image,cv.COLOR_BGR2GRAY)
cv.imwrite('images/res.png',grayImage)
flatImage=grayImage.flatten()
sendImage=[[grayImage.shape[0]],[grayImage.shape[1]],list(flatImage)]
sendImage=[x for xs in sendImage for x in xs]
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    print(1)
    s.sendall(bytearray(sendImage))
    data = s.recv(4096)
    data=int.from_bytes(data,byteorder='big',signed=True)


print('Received' +str(data))