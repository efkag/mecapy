#!/usr/bin/python
import serial
import numpy as np
import time



try:
    arduino = serial.Serial(port='/dev/ttyACM0', baudrate=9600, write_timeout=0)
    open=True
except:
    open=False
    pass
#open=False
if open:
    if arduino.is_open:
        print('Serial port to arduino is open')
    else:
        print('Serial port has failed to open, just printing outputs')
        open=False
        


'''
motor order/layout
idx0 -> front right (fr)
idx1 -> front left (frl
idx2 -> back right (br)
idx3 -> back left (bl)
'''

def test():
    mtrs = np.array([1, 1, 1, 1, 0, 0, 254, 0, 255], dtype=np.uint8)
    arduino.write(mtrs)
    for i in range(10):
        if open:
            arduino.write(mtrs)
            time.sleep(.5)

def forward(gains):
    drive([1,1,1,1],gains)
    
def back(gains):
    drive([0,0,0,0],gains)

def left(gains):
    drive([0,1,0,1],gains)
    
def right(gains):
    drive([1,0,1,0],gains)

def stop():
    mtrs = np.array([0, 0, 0, 0, 0, 0, 0, 0, 255], dtype=np.uint8)
    if open:
        arduino.write(mtrs)


def validate_comands(a):
    assert len(a) == 4, 'the comands have to be 4 numbers for the signs and 4 numbers for the gains'
    if isinstance(a, list):
        return np.array(a, dtype=np.uint8)
    return a.astype(np.uint8)
    

def drive(signs, gains):
    signs = validate_comands(signs)
    gains = validate_comands(gains)
    mtrs = np.zeros(9, dtype=np.uint8)
    mtrs[:4] = signs
    mtrs[4:8] = gains
    mtrs[8] = 255
    #print(mtrs)
    if open:
        arduino.write(mtrs)

stop()
time.sleep(2)
'''

drive([1, 1, 1, 1], [254, 254, 254, 254])
time.sleep(5)

for i in range(5):
    drive([1, 1, 1, 1], [254, 254, 254, 254])
    time.sleep(.5)
print('stopping')
stop()
time.sleep(5)
drive([1, 1, 1, 1], [254, 254, 254, 254])
drive([1, 1, 1, 1], [254, 254, 254, 254])
drive([1, 1, 1, 1], [254, 254, 254, 254])
stop()
time.sleep(5)
'''
