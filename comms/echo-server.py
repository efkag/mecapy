# echo-server.py

import socket
import numpy as np
import cv2 as cv

HOST = "192.168.1.5"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print("Connected")
        while True:
            data = conn.recv(4096)
            if data:
                back=list(data)
                print(len(data))
                newarray=np.array(back[2:]).reshape((back[0],back[1]))
                headingplacehold=newarray.shape[0]
                cv.imwrite('images/rec.png', newarray)
                conn.sendall(headingplacehold.to_bytes(3,byteorder='big',signed=True))
            if not data:
                s.close()
                break

            