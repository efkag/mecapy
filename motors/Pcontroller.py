#!/usr/bin/python
import serial
import numpy as np
import time
import motors

'''
Uses a P controller to adjust gain relative to heading deviation
'''

class deg2gain():
    def __init__(self):
        self.maxGain=254
        self.minGain=50 # below this, the motors are operating too slow to gain any traction.
        self.pFactor=0.5
        self.acceptableHeading=5 #not sure if this is the right place really, but here for now

    # Formulated such that the setpoint is 0 degrees 
    # and that the error is the heading required to reach 0 degrees
    # i.e the difference between 0 and heading given at the minimum

    def P_controller(self,degError):
        return(self.pFactor*abs(degError))

    def convert(self,degError):
        if abs(degError)>self.acceptableHeading:
            gain=self.P_controller(degError)
            gain if gain<self.maxGain else self.maxGain
            gain if gain>self.minGain else self.minGain
        else:
            gain=0
        return(gain)



'''
Test code - as degree error reduces, gain on the motors should also reduce
'''
#for degError in range(-180,0):
#    print(degError)
#    gain=deg2gain().convert(degError)
#    gains=[abs(gain)]*4
#    print(gain)
#    print(gains)
#    if np.sign(gain)<0:
#        motors.left(gains)
#        time.sleep(0.5)
#    elif np.sign(gain)>0:
#        motors.right(gains)
#        time.sleep(0.5)
#    else:
#        motors.stop()
#        break

		
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