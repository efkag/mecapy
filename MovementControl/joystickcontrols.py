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

deadzone=10
maxGain=130

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

##### ALOT OF NUMBERS HERE THAT NEED TO BE IN A CONFIG

def power(state,keyvalue):
    
    if keyvalue[0]>(128-deadzone) and keyvalue[0]<(128+deadzone):
        return(turn(state,keyvalue[1]))
    if keyvalue[1]>(128-deadzone) and keyvalue[1]<(128+deadzone):
        return(forward(state,keyvalue[0]))
        
    if keyvalue[0]<128:
        drive=1
    else:
        drive=0
    
    forwardgain=calcForwardGain(keyvalue[0])
    
    if keyvalue[1]<(128-deadzone):
        turngain=int(np.interp(255-abs(keyvalue[1]), [128, 254], [0, 125]))
        motors.drive([drive,drive,drive,drive],[forwardgain,turngain,forwardgain,turngain])

        
    elif keyvalue[1]>(128+deadzone):
        turngain=int(np.interp(abs(keyvalue[1]), [128, 254], [0, 125]))
        motors.drive([drive,drive,drive,drive],[turngain,forwardgain,turngain,forwardgain])
    

    return(state)

def calcForwardGain(keyvalue):
    if keyvalue < 128:
        gain=int(np.interp(255-abs(keyvalue), [128, 254], [0, maxGain]))
    else:
        gain=int(np.interp(abs(keyvalue), [128, 254], [0, maxGain]))
    return(gain)
    
def forward(state,keyvalue):
    if keyvalue < 128:
        gain=calcForwardGain(keyvalue)
        motors.forward([gain]*4)
    else:
        gain=calcForwardGain(keyvalue)
        motors.back([gain]*4)
    return(state)

def turn(state,keyvalue):
    #print('turning')
    if keyvalue < 128:
        #print(state, 'turning left')
        gain= int(np.interp(255-abs(keyvalue), [128, 254], [0, 80]))
        motors.left([gain]*4)
    else:
        #print(state, ' turning right')
        gain=int(np.interp(abs(keyvalue), [128, 254], [0, 80]))
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
    'ABS_Y' : forward,
    'ABS_RX' : None,
    'ABS_RY' : None,
    'ABS_HAT0X': None,
    'ABS_HAT0Y': None,
    'TOT':power,
}

'''
keystatus={
    "ABS_Y":128, #left analog, front to back
    "ABS_Z":128 # right analog, left to right
    }


def updateKeyStatus(event):
    if event.ev_type=='Absolute' or event.ev_type=='Key':
        keystatus[event.code]=event.state
    print(keystatus)
while True:
    events = inputs.get_gamepad()
    for event in events:
        updateKeyStatus(event)
        #print(event.ev_type, event.code, event.state)
        #f_call = event_lut.get(event.code)
        #if callable(f_call):
            #f_call(event.state)
'''

def keys2commands(keysdown):
    commands=keysdown.copy()
    if 'ABS_Y' in commands and 'ABS_Z' in commands:
        commands['TOT']=[keysdown['ABS_Y'],keysdown['ABS_Z']]
        commands.pop('ABS_Y')
        commands.pop('ABS_Z')
    return(commands)
        
    

def action(keysdown,movementState):
    if movementState['live']==1:
        commands=keys2commands(keysdown)
        #print(commands)
        for command in commands:
            #print(command)
            f_call=event_lut.get(command)
            if callable(f_call):
                movementState=f_call(movementState,commands[command])
    return(movementState)
