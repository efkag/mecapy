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
        self.maxGain=180
        self.minGain=42 # below this, the motors are operating too slow to gain any traction.
        self.pFactor=0.5
        self.iFactor=0
        self.dFactor=0
        self.acceptableHeading=3 #not sure if this is the right place really, but here for now
        self.cumuError=0
        self.lastError=0
        self.startTime=time.time()

    # Formulated such that the setpoint is 0 degrees 
    # and that the error is the heading required to reach 0 degrees
    # i.e the difference between 0 and heading given at the minimum

    def P_controller(self,degError):
        currenttime=time.time()
        difftime=currenttime-self.startTime
        
        self.cumuError=self.cumuError+abs(degError)*difftime
        self.rateError=(degError-self.lastError)/difftime
        
        gain=self.pFactor*abs(degError)+self.iFactor*self.cumuError+self.dFactor*self.rateError
        
        gain
        self.lastError=degError
        self.startTime=currenttime
        return(int(np.interp(abs(gain), [0, 254], [self.minGain, self.maxGain])))

    def convert(self,degError):
        if abs(degError)>self.acceptableHeading:
            gain=self.P_controller(degError)

            if gain<self.maxGain:
                gain=gain
            else: 
                gain=self.maxGain
                
            if gain>self.minGain:
                gain=gain
            else:
                gain=self.minGain
                
            #print('de',degError)
            #print('g',gain)
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
