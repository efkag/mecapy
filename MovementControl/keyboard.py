import inputs
import sys
import numpy as np
import os

path = os.path.join(os.path.dirname(__file__), os.pardir)
fwd = os.path.dirname(__file__)
sys.path.append(path)

from motors import motors


'''
Default alternative to joystick incase there are issues - 
Joystick can be difficult as they are less standardized
'''

def kill_robot(state):
    state['live']=0
    motors.stop()
    print('terminating')
    return(state)

def Power(state,direction):
    print(state, ' motor gain' )
    if direction ==1:
        gain=int(np.interp(abs(state['throttle']), [0, 3000], [50, 254]))
        motors.forward([gain]*4)
        print('forward', state['throttle'])

    else:
        print('not coded yet')
        print('back', state['throttle'])

def PowerForward(state):
    Power(state,1)
    return(state)

def PowerBack(state):
    Power(state,-1)
    return(state)

def TurnLeft(state):
    motors.left([254]*4)
    return(state)

def TurnRight(state):
    motors.right([254]*4)
    return(state)

def throttle(state,change):
    state['throttle']=state['throttle']+change
    if state['throttle']>=3000:
        state['throttle']=3000
    if state['throttle']<0:
        state['throttle']=0
    return(state)

def ThrottleUp(state):
    state=throttle(state,1)
    return(state)

def ThrottleDown(state):
    state=throttle(state,-1)
    return(state)


event_lut = {
    'KEY_W': PowerForward,
    'KEY_A' : TurnLeft,
    'KEY_D' : TurnRight,
    'KEY_S' : PowerBack,
    'KEY_UP':ThrottleUp,
    'KEY_DOWN':ThrottleDown,
    'KEY_X':kill_robot}




def action(keysdown,movementState):
    #print(keysdown)
    if movementState['live']==1:
        for key in keysdown.copy():
            f_call=event_lut.get(key[0])
            if callable(f_call):
                movementState=f_call(movementState)
    return(movementState)
    
'''
print(inputs.devices.keyboards) 
# from this make sure to pick the right keyboard
# can check events with 'libinput debug-events' in terminal
keyboardIdx=1
while True:
    events = inputs.get_key(keyboardIdx=keyboardIdx)
    print(len(events))
    for event in events:
        print(event.ev_type, event.code, event.state)
        #f_call = event_lut.get(event.code)
        #if callable(f_call):
            #f_call(event.state)
            '''

