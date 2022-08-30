import inputs
import sys
import numpy as np
import os
import sys

path = os.path.join(os.path.dirname(__file__), os.pardir)
fwd = os.path.dirname(__file__)
sys.path.append(path)

from motors import motors

print(inputs.devices)
for f in inputs.devices:
     print(f)

print(inputs.devices.gamepads) 

driving_state = True
pause_state = False

def reset(state,keyvalue):
    print('stop the mmotors')
    return(state)

def pause(state,keyvalue):
    if state==1:
        print('pause the robot')
    return(state)

def start_rec(state,keyvalue):
    if state==1:
        print('started recording')
    return(state)

def kill_robot(state,keyvalue):
    state['live']=0
    motors.stop()
    print('terminating')
    return(state)

def power(state,keyvalue):
    #print(state, ' motor gain' )
    print(keyvalue)
    if keyvalue < 128:
        gain=int(np.interp(255-abs(keyvalue), [128, 254], [0, 254]))
        motors.forward([gain]*4)
    else:
        print('back', int(np.interp(abs(keyvalue), [128, 254], [0, 254])))

    return(state)

def turn(state,keyvalue):
    print('turning')
    if keyvalue < 128:
        print(state, 'turning left')
        gain= int(np.interp(255-abs(keyvalue), [128, 254], [0, 254]))
        motors.left([gain]*4)
    else:
        print(state, ' turning right')
        gain=int(np.interp(abs(keyvalue), [128, 254], [0, 254]))
        motors.right([gain]*4)
        
    return(state)

event_lut = {
    'BTN_MODE': reset,
    'BTN_START' : None,
    'BTN_NORTH' : kill_robot,
    'BTN_SOUTH' : pause,
    'BTN_EAST' : None,
    'BTN_WEST' : None,
    'BTN_TR' : None,
    'BTN_TL' : None,
    'BTN_THUMBR' : None,
    'BTN_THUMBL' : None,
    'ABS_Z' : turn,
    'ABS_RZ' : None,
    'ABS_X' : None,
    'ABS_Y' : power,
    'ABS_RX' : None,
    'ABS_RY' : None,
    'ABS_HAT0X': None,
    'ABS_HAT0Y': None,
}

'''
while True:
    events = inputs.get_gamepad()
    for event in events:
        print(event.ev_type, event.code, event.state)
        f_call = event_lut.get(event.code)
        if callable(f_call):
            f_call(event.state)
'''

def action(keysdown,movementState):
    #print(keysdown)
    if movementState['live']==1:
        for key in keysdown.copy():
            f_call=event_lut.get(key[0])
            if callable(f_call):
                movementState=f_call(movementState,key[1])
    return(movementState)