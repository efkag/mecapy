import inputs
import sys
import numpy as np
print(inputs.devices.gamepads)

driving_state = True
pause_state = False

def reset(state):
    print('stop the mmotors')

def pause(state):
    if state==1:
        print('pause the robot')

def start_rec(state):
    if state==1:
        print('started recording')

def kill_robot(state):
    if state==1:
        print('program stopped')
        sys.exit()

def power(state):
    print(state, ' motor gain' )
    if state < 128:
        print('forward', int(np.interp(abs(state), [0, 32768], [0, 254])))
    else:
        print('back', int(np.interp(abs(state), [0, 32768], [0, 254])))

def turn(state):
    if state < 128:
        print(state, 'turning left')
        print('turning left', int(np.interp(abs(state), [0, 32768], [0, 254])))
    else:
        print(state, ' turning right')
        print('turning right', int(np.interp(abs(state), [0, 32768], [0, 254])))

event_lut = {
    'BTN_MODE': reset,
    'BTN_START' : None,
    'BTN_NORTH' : kill_robot,
    'BTN_SOUTH' : pause,
    'BTN_EAST' : start_rec,
    'BTN_WEST' : None,
    'BTN_TR' : None,
    'BTN_TL' : None,
    'BTN_THUMBR' : None,
    'BTN_THUMBL' : None,
    'ABS_Z' : None,
    'ABS_RZ' : None,
    'ABS_X' : None,
    'ABS_Y' : power,
    'ABS_RX' : turn,
    'ABS_RY' : None,
    'ABS_HAT0X': None,
    'ABS_HAT0Y': None,
}

while True:
    events = inputs.get_gamepad()
    for event in events:
        print(event.ev_type, event.code, event.state)
        f_call = event_lut.get(event.code)
        if callable(f_call):
            f_call(event.state)